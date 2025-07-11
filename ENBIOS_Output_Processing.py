import pandas as pd
import os
import re


def transform_data_to_powerbi(data: pd.DataFrame,
                              output_path: str,
                              name_cleaning: bool = False):
    # -------------------------------------------------------------
    # A. housekeeping
    # -------------------------------------------------------------
    #  drop duplicated ".1" columns (intensive), if any, and COPY to avoid view-warning
    data = data.loc[:, ~data.columns.str.contains(r"\.1$", regex=True)].copy()
    #  get level columns in numeric order (lvl_0, lvl_1, …)
    level_names = sorted(
        [c for c in data.columns if c.startswith("lvl_")],
        key=lambda s: int(s.split("_")[1])
    )
    # -------------------------------------------------------------
    # B. forward-fill each level only **inside its parent group**
    # -------------------------------------------------------------
    for i, lvl in enumerate(level_names):
        parents = level_names[:i]  # higher levels
        if parents:
            data[lvl] = data.groupby(parents, sort=False)[lvl].ffill()
        else:
            data[lvl] = data[lvl].ffill()
    #   drop any row that still has an empty level (prevents mismatches)
    data = data.dropna(subset=level_names)
    #   clean names of technologies and levels
    if name_cleaning:
        def strip_suffix(x: str) -> str:
            if not isinstance(x, str):
                return x

            # Normalize onsite/offsite
            x = x.replace("-onsite", "_onsite").replace("-offsite", "_offsite")

            # Capture and remove known tail patterns (e.g., electricity carrier prod chains, regions)
            x = re.sub(r'_electricity.*$', '', x)
            x = re.sub(r'(_carrier_prod.*|_nuts\d+|_region.*)$', '', x)

            return x

        for col in level_names:
            data[col] = data[col].map(strip_suffix)

    # -------------------------------------------------------------
    # C. long transformation
    # -------------------------------------------------------------
    unit_cols = [c for c in data.columns if "unit" in c]
    magnitude_cols = [c for c in data.columns if "magnitude" in c]
    unit_long = (
        pd.melt(data, id_vars=level_names,
                value_vars=unit_cols, var_name="variable", value_name="unit")
        .assign(variable=lambda d: (
            d["variable"]
            .str.replace("_unit$", "", regex=True)
            .str.replace("^results_", "", regex=True)
        ))
    )
    mag_long = (
        pd.melt(data, id_vars=level_names,
                value_vars=magnitude_cols, var_name="variable", value_name="value")
        .assign(variable=lambda d: (
            d["variable"]
            .str.replace("_magnitude$", "", regex=True)
            .str.replace("^results_", "", regex=True)
        ))
    )
    data_long = pd.merge(unit_long, mag_long, on=level_names + ["variable"])
    # keep output_0 wide
    out0 = (
        data_long.loc[data_long["variable"] == "output_0",
                      level_names + ["value"]]
        .rename(columns={"value": "output_0"})
    )
    data_long = data_long[data_long["variable"] != "output_0"]
    data_long = data_long.merge(out0, on=level_names, how="left")
    data_long.to_csv(output_path, index=False)

#loading data
input_dir = r'C:\Users\mique\PycharmProjects\LIVEN_onsite_offsite_github\example_data'
baseline_input_path = os.path.join(input_dir, 'enbios_output_baseline_nuts2.csv')
#pniec_input_path = os.path.join(input_dir, 'enbios_output_pniec_nuts2.csv')
data_bsl = pd.read_csv(baseline_input_path)
#data_pniec = pd.read_csv(pniec_input_path)

#define output path
baseline_output_path = os.path.join(input_dir, 'operation_2024_nuts2_output.csv')
pniec_output_path = os.path.join(input_dir, 'operation_pniec_2030_nuts2_output.csv')

transform_data_to_powerbi(data_bsl, baseline_output_path, name_cleaning=True)
#transform_data_to_powerbi(data_pniec, pniec_output_path, name_cleaning=True)
