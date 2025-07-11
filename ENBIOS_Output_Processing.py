import pandas as pd
import os
import re

LOC_MAPPING = {'ES_1': 'Andalucía',
               'ES_2': 'Aragón',
               'ES_3': 'Principado de Asturias',
               'ES_4': 'Cantabria',
               'ES_5': 'Castilla-La Mancha',
               'ES_6': 'Castilla y León',
               'ES_7': 'Cataluña',
               'ES_8': 'Comunidad de Ceuta',
               'ES_9': 'Comunidad de Madrid',
               'ES_10': 'Comunidad Valenciana',
               'ES_11': 'Extremadura',
               'ES_12': 'Galicia',
               'ES_13': 'Islas Baleares',
               'ES_14': 'Islas Canarias',
               'ES_15': 'La Rioja',
               'ES_16': 'Comunidad de Melilla',
               'ES_17': 'Región de Murcia',
               'ES_18': 'Comunidad Foral de Navarra',
               'ES_19': 'País Vasco',
               'ES': 'Nacional'
               }


def transform_data_to_powerbi(data: pd.DataFrame,
                              output_path: str,
                              regions: bool = False,
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

    # change '_ES_1' type lables for Autonomous Community name, if necessary
    if regions:
        # Extract region_ID from lvl_1 (e.g., 'foo_ES_5' → 'ES_5')
        data_long["region_ID"] = (
            data_long["lvl_1"].str.extract(r"(ES_\d+)", expand=False)
        )

        # Drop lvl_1
        data_long = data_long.drop(columns=["lvl_1"])
        level_names.remove("lvl_1")

        # Insert region_ID after last level column
        last_lvl_idx = max([data_long.columns.get_loc(col) for col in level_names])
        cols = list(data_long.columns)
        cols.insert(last_lvl_idx + 1, cols.pop(cols.index("region_ID")))
        data_long = data_long[cols]

        # Map region_ID to region_name using global LOC_MAPPING
        data_long["region_name"] = data_long["region_ID"].map(LOC_MAPPING)

        # Insert region_name right after region_ID
        idx_id = data_long.columns.get_loc("region_ID")
        cols = list(data_long.columns)
        cols.insert(idx_id + 1, cols.pop(cols.index("region_name")))
        data_long = data_long[cols]

        # Trim everything after '_ES' in all string fields (except region_ID)
        for col in data_long.select_dtypes(include="object").columns:
            if col != "region_ID":
                data_long[col] = data_long[col].str.replace(r"_ES.*$", "", regex=True)

        # rename lvl_0 to lvl_1
        if "lvl_0" in data_long.columns:
            data_long = data_long.rename(columns={"lvl_0": "lvl_1"})

    # change
    data_long.to_csv(output_path, index=False)

#loading data
input_dir = r'C:\Users\mique\PycharmProjects\LIVEN_onsite_offsite_github\example_data'
baseline_input_path = os.path.join(input_dir, 'enbios_output_baseline_nuts2.csv')
pniec_input_path = os.path.join(input_dir, 'enbios_output_pniec_nuts2.csv')
data_bsl = pd.read_csv(baseline_input_path)
data_pniec = pd.read_csv(pniec_input_path)

#define output path
baseline_output_path = os.path.join(input_dir, 'operation_2024_nuts2_output.csv')
pniec_output_path = os.path.join(input_dir, 'operation_pniec_2030_nuts2_output.csv')

transform_data_to_powerbi(data_bsl, baseline_output_path, name_cleaning=True, regions=True)
transform_data_to_powerbi(data_pniec, pniec_output_path, name_cleaning=True, regions=True)
