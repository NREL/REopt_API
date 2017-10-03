import os
import json
from api_definitions import outputs
from dispatch import ProcessOutputs

class Results:

    # file names
    file_proforma = 'ProForma.xlsm'
    file_dispatch = 'Dispatch.csv'

    # time outputs (scalar)
    time_steps_per_hour = 1

    bau_attributes = [
        "lcc",
        "year_one_energy_cost",
        "year_one_demand_cost",
        "year_one_fixed_cost",
        "year_one_min_charge_adder",
        "total_energy_cost",
        "total_demand_cost",
        "total_fixed_cost",
        "total_min_charge_adder",
    ]

    def __init__(self, path_templates, path_output, path_output_bau, path_static, year):
        """

        :param path_templates: path to proForma template
        :param path_output: path to scenario output dir
        :param path_output_bau: path to bau results json
        :param path_static: path to copy proForma to for user download
        :param year: load_year
        """

        with open(os.path.join(path_output, "REopt_results.json"), 'r') as f:
            results_dict = json.loads(f.read())

        with open(os.path.join(path_output_bau, "REopt_results.json"), 'r') as f:
            results_dict_bau = json.loads(f.read())

        # add bau outputs to results_dict
        for k in Results.bau_attributes:
            results_dict[k+'_bau'] = results_dict_bau[k]

        # set missing outputs to None
        for k in outputs().iterkeys():
            results_dict.setdefault(k, None)

        # b/c of PV & PVNM techs in REopt, if both are zero then no value is written to REopt_results.json
        if results_dict['pv_kw'] is None:
            results_dict['pv_kw'] = 0

        results_dict['npv'] = results_dict['lcc_bau'] - results_dict['lcc']

        # dispatch
        po = ProcessOutputs(path_output, year)
        results_dict['year_one_grid_to_load_series'] = po.get_grid_to_load()
        results_dict['year_one_grid_to_battery_series'] = po.get_grid_to_batt()
        results_dict['year_one_pv_to_load_series'] = po.get_pv_to_load()
        results_dict['year_one_pv_to_battery_series'] = po.get_pv_to_batt()
        results_dict['year_one_pv_to_grid_series'] = po.get_pv_to_grid()
        results_dict['year_one_battery_soc_series'] = po.get_soc(results_dict['batt_kwh'])
        results_dict['time_steps_per_hour'] = len(results_dict['year_one_grid_to_load_series'])
        results_dict['year_one_energy_cost_series'] = po.get_energy_cost()
        results_dict['year_one_demand_cost_series'] = po.get_energy_cost()
        results_dict['year_one_electric_load_series'] = po.get_load_profile()
        results_dict['year_one_battery_to_load_series'] = po.get_batt_to_load()
        results_dict['year_one_battery_to_grid_series'] = po.get_batt_to_grid()
        results_dict['year_one_wind_to_load_series'] = po.get_wind_to_load()
        results_dict['year_one_wind_to_battery_series'] = po.get_wind_to_batt()
        results_dict['year_one_wind_to_grid_series'] = po.get_wind_to_grid()

        self.results_dict = results_dict
        self.results_dict_bau = results_dict_bau
        self.path_templates = path_templates
        self.path_output = path_output
        self.path_static = os.path.join(path_static, self.file_proforma)
        self.path_proforma = os.path.join(path_output, self.file_proforma)
        self.year = year

    def get_output(self):
        output_dict = dict()
        for k in outputs().iterkeys():
            output_dict[k] = self.results_dict[k]
        return output_dict

    def is_system(self):
        system = False
        if self.results_dict['pv_kw'] > 0 or self.results_dict['batt_kw'] > 0:
            system = True
        return system
