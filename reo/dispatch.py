import os
import numpy as np
import pandas as pd


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

    def __init__(self, path_outputs, year=2017):
        """

        :param path_outputs: path to REopt output dir
        :param year: first year of analysis
        """

        self.path_elec_from_store = os.path.join(path_outputs, "ElecFromStore.csv")
        self.path_elec_to_store = os.path.join(path_outputs, "ElecToStore.csv")
        self.path_load = os.path.join(path_outputs, "Load.csv")
        self.path_peak_demands = os.path.join(path_outputs, "PeakDemands.csv")
        self.path_production = os.path.join(path_outputs, "Production.csv")
        self.path_stored_energy = os.path.join(path_outputs, "StoredEnergy.csv")
        self.path_energy_cost = os.path.join(path_outputs, "energy_cost.txt")
        self.path_demand_cost = os.path.join(path_outputs, "demand_cost.txt")
        self.path_grid_to_load = os.path.join(path_outputs, "GridToLoad.csv")
        self.path_grid_to_batt = os.path.join(path_outputs, "GridToBatt.csv")
        self.path_pv_to_load = os.path.join(path_outputs, "PVtoLoad.csv")
        self.path_pv_to_batt = os.path.join(path_outputs, "PVtoBatt.csv")
        self.path_pv_to_grid = os.path.join(path_outputs, "PVtoGrid.csv")
        self.path_wind_to_load = os.path.join(path_outputs, "WINDtoLoad.csv")
        self.path_wind_to_batt = os.path.join(path_outputs, "WINDtoBatt.csv")
        self.path_wind_to_grid = os.path.join(path_outputs, "WINDtoGrid.csv")
        self.year = year

    def get_batt_to_grid(self):  # this was not defined in original dispatch.py
        return None

    def get_batt_to_load(self):

        if os.path.isfile(self.path_elec_from_store):
            return self._load_csv(self.path_elec_from_store)
        return None

    def get_energy_cost(self):

        if os.path.isfile(self.path_energy_cost):
            return self._load_csv(self.path_energy_cost)
        return None

    def get_demand_cost(self):

        if os.path.isfile(self.path_demand_cost):
            return self._load_csv(self.path_demand_cost)
        return None

    def get_soc(self, batt_kwh):

        if os.path.isfile(self.path_stored_energy):
            stored_energy = self._load_csv(self.path_stored_energy)
            return [float(se) / batt_kwh for se in stored_energy]
        return None

    def get_grid_to_load(self):

        if os.path.isfile(self.path_grid_to_load):
            return self._load_csv(self.path_grid_to_load)
        return None

    def get_grid_to_batt(self):

        if os.path.isfile(self.path_grid_to_batt):
            return self._load_csv(self.path_grid_to_batt)
        return None

    def get_pv_to_load(self):

        if os.path.isfile(self.path_pv_to_load):
            return self._load_csv(self.path_pv_to_load)
        return None

    def get_pv_to_grid(self):

        if os.path.isfile(self.path_pv_to_grid):
            return self._load_csv(self.path_pv_to_grid)
        return None

    def get_pv_to_batt(self):

        if os.path.isfile(self.path_pv_to_batt):
            return self._load_csv(self.path_pv_to_batt)
        return None

    def get_wind_to_load(self):

        if os.path.isfile(self.path_wind_to_load):
            return self._load_csv(self.path_wind_to_load)
        return None

    def get_wind_to_grid(self):

        if os.path.isfile(self.path_wind_to_grid):
            return self._load_csv(self.path_wind_to_grid)
        return None

    def get_wind_to_batt(self):

        if os.path.isfile(self.path_wind_to_batt):
            return self._load_csv(self.path_wind_to_batt)
        return None

    def get_load_profile(self):

        if os.path.isfile(self.path_load):
            return self._load_csv(self.path_load)
        return None

    def _load_csv(self, path):
        """
        internal method for loading dispatch csv's into lists
        :param path: path to csv file
        :return: return list of params
        """
        l = list()
        with open(path, 'r') as f:
            for line in f.readlines():
                l.append(float(line))
        return l




