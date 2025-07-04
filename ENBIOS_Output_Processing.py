#loading data

import pandas as pd
import os

#loading data
data_bsl = pd.read_csv(datadir + '/operation_baseline_2024.csv')

data_pniec = pd.read_csv(datadir + '/operation_pniec_2030.csv')

data = data_pniec
#Filling names with the value of the row with the lower index
data['lvl_0'] = data['lvl_0'].ffill()
data['lvl_1'] = data['lvl_1'].ffill()
data['lvl_2'] = data['lvl_2'].ffill()
data['lvl_3'] = data['lvl_3'].ffill()
data['lvl_4'] = data['lvl_4'].ffill()

# extracting the rows with values in lvl_5
data_lvl_5 = data[data['lvl_5'].notna()]

# transforming to long data
# Filter columns containing "unit" and "magnitude"
unit_columns = [col for col in data_lvl_5.columns if 'unit' in col]
magnitude_columns = [col for col in data_lvl_5.columns if 'magnitude' in col]

# Transform "unit" columns to long format
data_unit_long = pd.melt(data_lvl_5, id_vars=['lvl_0', 'lvl_1', 'lvl_2', 'lvl_3', 'lvl_4', 'lvl_5'],
                         value_vars=unit_columns, var_name='variable', value_name='unit')
#remove from "variable" the "_unit" part
data_unit_long['variable'] = data_unit_long['variable'].str.replace('_unit', '', regex=False)
#remove the "results_" part
data_unit_long['variable'] = data_unit_long['variable'].str.replace('results_', '', regex=False)



# Transform "magnitude" columns to long format
data_magnitude_long = pd.melt(data_lvl_5, id_vars=['lvl_0', 'lvl_1', 'lvl_2', 'lvl_3', 'lvl_4', 'lvl_5'],
                              value_vars=magnitude_columns, var_name='variable', value_name='value')
#remove from "variable" the "_magnitude" part
data_magnitude_long['variable'] = data_magnitude_long['variable'].str.replace('_magnitude', '', regex=False)
#remove the "results_" part
data_magnitude_long['variable'] = data_magnitude_long['variable'].str.replace('results_', '', regex=False)


#merge tables
data_long = pd.merge(data_unit_long, data_magnitude_long, on=['lvl_0', 'lvl_1', 'lvl_2', 'lvl_3', 'lvl_4', 'lvl_5', 'variable'])

#save table
data_long.to_csv(outputdir + '/results_pniec_long.csv', index=False)

