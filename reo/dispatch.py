import os

import numpy as np
import pandas as pd

from datetime import datetime
from calendar import monthrange


def resample(pd_series_data, factor, index, interpolate=False):
    y_interp = []
    n_data = len(pd_series_data)

    if interpolate:

        '''
        file_data = open("Data.txt", 'w')
        for d in range(0, n_data):
            file_data.write(str(pd_series_data.iloc[d]) + "\n")
        file_data.close()
        '''
        x_data = range(0, n_data)
        x_interp = []
        for i in range(0, n_data):
            for j in range(0, factor):
                x_interp.append(float(x_data[i]) + float(j) / factor)
        y_data = pd_series_data.tolist()
        y_interp = np.interp(x_interp, x_data, y_data)
        '''
        file_interp = open("Interpolated", 'w')
        for d in range(0, len(y_interp)):
            file_interp.write(str(y_interp[d]) + "\n")
        '''
    for i in range(0, n_data):
        for f in range(0, factor):
            if not interpolate:
                y_interp.append(pd_series_data.iloc[i])

    return pd.Series(y_interp, index=index)


class ProcessOutputs:

    # paths
    path_outputs = []
    path_calc_output = []
    path_demand = []
    path_dispatch_hourly = []
    path_elec_from_store = []
    path_elec_penalty = []
    path_elec_to_store = []
    path_load = []
    path_peak_demands = []
    path_production = []
    path_reo_results = []
    path_stored_energy = []
    path_prod_factors = []
    path_hourly_rate_summary = []

    # parameters
    steps_per_hour = 1
    max_steps_per_hour = 4
    year = []
    resample_factor = []

    system = False
    pv_system = False
    battery_system = False
    generator_system = False
    grid_system = False

    batt_kwh = 0

    pv_in_interval = False
    battery_in_interval = False
    generator_in_interval = False
    grid_in_interval = False
    dual_pv_batt_gen = False

    # dataframes and series
    df_calc_output = []
    df_stored_energy = []
    date_range = []
    df_xpress_output = []

    tech_list = list()

    def __init__(self, df_results_summary, path_outputs, file_output, year=2015, resample_factor=1):

        self.path_outputs = path_outputs
        self.path_dispatch_output = os.path.join(self.path_outputs, file_output)
        self.path_dispatch_hourly = os.path.join(self.path_outputs, "DispatchHourly.csv")
        self.path_elec_from_store = os.path.join(self.path_outputs, "ElecFromStore.csv")
        self.path_elec_to_store = os.path.join(self.path_outputs, "ElecToStore.csv")
        self.path_load = os.path.join(self.path_outputs, "Load.csv")
        self.path_peak_demands = os.path.join(self.path_outputs, "PeakDemands.csv")
        self.path_production = os.path.join(self.path_outputs, "Production.csv")
        self.path_stored_energy = os.path.join(self.path_outputs, "StoredEnergy.csv")
        self.path_hourly_rate_summary = os.path.join(self.path_outputs, "HourlyRateSummary.csv")

        self.year = year
        self.resample_factor = resample_factor
        self.populate_techs(df_results_summary)

        if self.battery_system or self.pv_system or self.grid_system or self.generator_system:
            self.setup_dates()
            self.load_xpress_results()

    def get_dispatch(self):
        return self.df_xpress_output

    def setup_dates(self):

        # setup dates
        frequency = str(int(round(60/self.steps_per_hour, 0))) + 'min'
        self.date_range = pd.date_range(start=datetime(self.year, 1, 1),
                                        periods=8760 * self.steps_per_hour,
                                        freq=frequency).to_datetime()

    def populate_techs(self, df):

        if 'Battery Capacity (kWh)' in df.columns:
            self.batt_kwh = float(df['Battery Capacity (kWh)'].values[0])
            if self.batt_kwh > 0:
                self.tech_list.append('BATT')
                self.battery_system = True
        if 'PVNM Size (kW)' in df.columns:
            if float(df['PVNM Size (kW)'].values[0]) > 0:
                self.tech_list.append('PVNM')
                self.pv_system = True
        if 'PV Size (kW)' in df.columns:
            if float(df['PV Size (kW)'].values[0]) > 0:
                self.tech_list.append('PV')
                self.pv_system = True
        if 'Year 1 Energy Supplied From Grid (kWh)' in df.columns:
            if float(df['Year 1 Energy Supplied From Grid (kWh)'].values[0]) > 0:
                self.tech_list.append('UTIL1')
                self.grid_system = True

    def load_xpress_results(self):

        # DispatchHourly.csv
        headers = ['Tech', 'FuelBin', 'Time', 'Dispatch', 'Power']
        dispatch = pd.read_csv(self.path_dispatch_hourly, header=None, names=headers)
        dispatch_list = dispatch['Tech'].unique()
        fuel_list = dispatch['FuelBin'].unique()
        time_steps = dispatch.shape[0] / (len(dispatch_list) * len(fuel_list))
        index = range(1, time_steps + 1, 1)

        d = {}

        output_column_headers = list()
        output_column_headers.append("Date")
        output_column_headers.append('Energy Cost ($/kWh)')
        output_column_headers.append('Demand Cost ($/kW)')
        output_column_headers.append('Electric load')

        # for now, disable annoying warnings (which are false positives)
        pd.options.mode.chained_assignment = None  # default='warn'

        if 'PVNM' in self.tech_list:
            pvnm = dispatch.loc[dispatch['Tech'] == 'PVNM']

            pvnm_to_batt = pvnm.loc[pvnm['FuelBin'] == '1S']
            pvnm_to_batt.loc[:, 'Index'] = index
            pvnm_to_batt.set_index('Index', inplace=True)

            pvnm_to_load = pvnm.loc[pvnm['FuelBin'] == '1R']
            pvnm_to_load.loc[:, 'Index'] = index
            pvnm_to_load.set_index('Index', inplace=True)

            pvnm_to_grid = pvnm.loc[pvnm['FuelBin'] == '1W']
            pvnm_to_grid.loc[:, 'Index'] = index
            pvnm_to_grid.set_index('Index', inplace=True)

            pvnm_to_gridx = pvnm.loc[pvnm['FuelBin'] == '1X']
            pvnm_to_gridx.loc[:, 'Index'] = index
            pvnm_to_gridx.set_index('Index', inplace=True)

            d['PV to battery'] = pvnm_to_batt['Power']
            d['PV to load'] = pvnm_to_load['Power']
            d['PV to grid'] = pvnm_to_grid['Power'] + pvnm_to_gridx['Power']

        if 'PV' in self.tech_list:
            pv = dispatch.loc[dispatch['Tech'] == 'PV']

            pv_to_batt = pv.loc[pv['FuelBin'] == '1S']
            pv_to_batt.loc[:, 'Index'] = index
            pv_to_batt.set_index('Index', inplace=True)

            pv_to_load = pv.loc[pv['FuelBin'] == '1R']
            pv_to_load.loc[:, 'Index'] = index
            pv_to_load.set_index('Index', inplace=True)

            pv_to_grid = pv.loc[pv['FuelBin'] == '1W']
            pv_to_grid.loc[:, 'Index'] = index
            pv_to_grid.set_index('Index', inplace=True)

            pv_to_gridx = pv.loc[pv['FuelBin'] == '1X']
            pv_to_gridx.loc[:, 'Index'] = index
            pv_to_gridx.set_index('Index', inplace=True)

            d['PV to battery'] = pv_to_batt['Power']
            d['PV to load'] = pv_to_load['Power']
            d['PV to grid'] = pv_to_grid['Power'] + pv_to_gridx['Power']

        if self.pv_system:
            output_column_headers.append('PV to battery')
            output_column_headers.append('PV to load')
            output_column_headers.append('PV to grid')

        if 'UTIL1' in self.tech_list:
            util1 = dispatch.loc[dispatch['Tech'] == 'UTIL1']

            grid_to_load = util1.loc[util1['FuelBin'] == '1R']
            grid_to_load.loc[:, 'Index'] = index
            grid_to_load.set_index('Index', inplace=True)

            grid_to_batt = util1.loc[util1['FuelBin'] == '1S']
            grid_to_batt.loc[:, 'Index'] = index
            grid_to_batt.set_index('Index', inplace=True)

            d['Grid to load'] = grid_to_load['Power']
            d['Grid to battery'] = grid_to_batt['Power']

            output_column_headers.append('Grid to load')
            output_column_headers.append('Grid to battery')

        if "GEN1" in self.tech_list:
            gen1 = dispatch.loc[dispatch['Tech'] == 'GEN1']

            gen_to_load = gen1.loc[gen1['FuelBin'] == '1R']
            gen_to_load.loc[:, 'Index'] = index
            gen_to_load.set_index('Index', inplace=True)

            gen_to_batt = gen1.loc[gen1['FuelBin'] == '1S']
            gen_to_batt.loc[:, 'Index'] = index
            gen_to_batt.set_index('Index', inplace=True)

            d['Generator to load'] = gen_to_load['Power']
            d['Generator to battery'] = gen_to_batt['Power']

            self.generator_system = True

        if "GEN1NM" in self.tech_list:
            gen1nm = dispatch.loc[dispatch['Tech'] == 'GEN1NM']

            gennm_to_load = gen1nm.loc[gen1nm['FuelBin'] == '1R']
            gennm_to_load.loc[:, 'Index'] = index
            gennm_to_load.set_index('Index', inplace=True)

            gennm_to_batt = gen1nm.loc[gen1nm['FuelBin'] == '1S']
            gennm_to_batt.loc[:, 'Index'] = index
            gennm_to_batt.set_index('Index', inplace=True)

            d['Generator to load'] = gennm_to_load['Power']
            d['Generator to battery'] = gennm_to_batt['Power']

            self.generator_system = True

        if self.generator_system:
            output_column_headers.append('Generator to load')
            output_column_headers.append('Generator to battery')

        if "BATT" in self.tech_list:

            # StoredEnergy.csv
            stored = pd.read_csv(self.path_stored_energy, header=None, names=['Stored energy'])
            stored.loc[:, 'Index'] = index
            stored.set_index('Index', inplace=True)
            d['Stored energy'] = stored['Stored energy']
            d['State of charge'] = 100 * stored['Stored energy'].divide(self.batt_kwh)

            # ElecFromStore.csv
            batt_to_load = pd.read_csv(self.path_elec_from_store, header=None, names=['Battery to load'])
            batt_to_load.loc[:, 'Index'] = index
            batt_to_load.set_index('Index', inplace=True)
            d['Battery to load'] = batt_to_load['Battery to load']

            output_column_headers.append('Stored energy')
            output_column_headers.append('State of charge')
            output_column_headers.append('Battery to load')

        # Load.csv
        load = pd.read_csv(self.path_load, header=None, names=['Load'])
        load.loc[:, 'Index'] = index
        load.set_index('Index', inplace=True)
        d['Electric load'] = load['Load']

        # Hourly rate summary
        rates = pd.read_csv(self.path_hourly_rate_summary)
        rates.loc[:, 'Index'] = index
        rates.set_index('Index', inplace=True)
        d['Energy Cost ($/kWh)'] = rates['Energy Cost ($/kWh)']
        d['Demand Cost ($/kW)'] = rates['Demand Cost ($/kW)']

        # Date time
        d['Date'] = self.date_range

        self.df_xpress_output = pd.DataFrame(data=d)
        numeric = self.df_xpress_output._get_numeric_data()
        numeric[numeric < 0] = 0
        self.df_xpress_output = self.df_xpress_output[output_column_headers]
        self.df_xpress_output.to_csv(os.path.join(self.path_dispatch_output))


