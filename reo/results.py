import os
import shutil
from api_definitions import *
import pro_forma_writer as pf
from dispatch import ProcessOutputs
from tastypie.exceptions import ImmediateHttpResponse
import json


class Results:

    # file names
    file_proforma = 'ProForma.xlsm'
    file_dispatch = 'Dispatch.csv'

    # time outputs (scalar)
    time_steps_per_hour = 1

    # time series labels - where are these used?
    label_year_one_electric_load_series = 'Electric load'
    label_year_one_pv_to_battery_series = 'PV to battery'
    label_year_one_pv_to_load_series = 'PV to load'
    label_year_one_pv_to_grid_series = 'PV to grid'
    label_year_one_grid_to_load_series = 'Grid to load'
    label_year_one_grid_to_battery_series = 'Grid to battery'
    label_year_one_battery_to_load_series = 'Battery to load'
    label_year_one_battery_to_grid_series = 'Battery to grid'
    label_year_one_battery_soc_series = 'State of charge'
    label_year_one_energy_cost_series = 'Energy Cost ($/kWh)'
    label_year_one_demand_cost_series = 'Demand Cost ($/kW)'

    bau_attributes = [
        "lcc",
        "year_one_energy_cost",
        "year_one_demand_cost",
        "total_energy_cost",
        "total_demand_cost",
    ]

    def __init__(self, path_templates, path_output, path_output_bau, path_static, economics, year):
        """

        :param path_templates: path to proForma template
        :param path_output: path to scenario output dir
        :param path_output_bau: path to bau results json
        :param path_static: path to copy proForma to for user download
        :param economics: economics.Economics object
        :param year: load_year
        """

        with open(os.path.join(path_output, "REopt_results.json"), 'r') as f:
            results_dict = json.loads(f.read())

        with open(os.path.join(path_output_bau, "REopt_results.json"), 'r') as f:
            results_dict_bau = json.loads(f.read())

        if not self.is_optimal(results_dict) and not self.is_optimal(results_dict_bau):
            raise ImmediateHttpResponse("No solution could be found for these inputs")

        # add bau outputs to results_dict
        for k in Results.bau_attributes:
            results_dict[k+'_bau'] = results_dict_bau[k]

        for k in outputs().iterkeys():
            setattr(self, k, None)
            results_dict.setdefault(k, None)

        results_dict['npv'] = results_dict['lcc_bau'] - results_dict['lcc']

        # dispatch
        po = ProcessOutputs(results_dict, path_output, self.file_dispatch, year)
        results_dict['year_one_grid_to_load_series'] = po.get_grid_to_load()
        results_dict['year_one_grid_to_battery_series'] = po.get_grid_to_batt()
        results_dict['year_one_pv_to_load_series'] = po.get_pv_to_load()
        results_dict['year_one_pv_to_battery_series'] = po.get_pv_to_batt()
        results_dict['year_one_pv_to_grid_series'] = po.get_pv_to_grid()
        results_dict['year_one_battery_soc_series'] = po.get_soc(results_dict['batt_kwh'])
        results_dict['time_steps_per_hour'] = len(results_dict['year_one_grid_to_load_series'])
        results_dict['year_one_energy_cost_series'] = po.get_energy_cost()
        results_dict['year_one_demand_cost_series'] = po.get_energy_cost()
        results_dict['year_one_electric_load_series'] = po.get_demand_cost()
        results_dict['year_one_battery_to_load_series'] = po.get_batt_to_load()
        results_dict['year_one_battery_to_grid_series'] = po.get_batt_to_grid()

        self.results_dict = results_dict
        self.results_dict_bau = results_dict_bau

        ####################################################

        self.path_templates = path_templates
        self.path_output = path_output
        self.path_static = os.path.join(path_static, self.file_proforma)
        self.path_proforma = os.path.join(path_output, self.file_proforma)
        self.economics = economics
        self.year = year


        self.generate_pro_forma()

    def copy_static(self):
        shutil.copyfile(self.path_proforma, self.path_static)

    @staticmethod
    def is_optimal(d):

        if 'status' in d.keys():
            status = str(d['status']).rstrip()
            # self.results_dict['status'] = status  # need to handle BAU
            return status == "Optimum found"
        return False

    def generate_pro_forma(self):

        cash_flow = pf.ProForma(self.path_templates, self.path_output, self.economics, self.results_dict)
        cash_flow.update_template()
        cash_flow.compute_cashflow()

        # make results consistent
        self.results_dict['irr'] = cash_flow.get_irr()
        self.results_dict['npv'] = cash_flow.get_npv()
        self.results_dict['lcc'] = cash_flow.get_lcc()

    def get_output(self):
        output_dict = dict()
        for k in outputs().iterkeys():
            output_dict[k] = self.results_dict[k]
        return output_dict
