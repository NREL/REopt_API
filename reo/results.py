import os
import json
from api_definitions import outputs
from nested_outputs import nested_output_definitions
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
        self.po = ProcessOutputs(path_output, year)
        results_dict['year_one_grid_to_load_series'] = self.po.get_grid_to_load()
        results_dict['year_one_grid_to_battery_series'] = self.po.get_grid_to_batt()
        results_dict['year_one_pv_to_load_series'] = self.po.get_pv_to_load()
        results_dict['year_one_pv_to_battery_series'] = self.po.get_pv_to_batt()
        results_dict['year_one_pv_to_grid_series'] = self.po.get_pv_to_grid()
        results_dict['year_one_battery_soc_series'] = self.po.get_soc(results_dict['batt_kwh'])
        results_dict['time_steps_per_hour'] = len(results_dict['year_one_grid_to_load_series'])
        results_dict['year_one_energy_cost_series'] = self.po.get_energy_cost()
        results_dict['year_one_demand_cost_series'] = self.po.get_demand_cost()
        results_dict['year_one_electric_load_series'] = self.po.get_load_profile()
        results_dict['year_one_battery_to_load_series'] = self.po.get_batt_to_load()
        results_dict['year_one_battery_to_grid_series'] = self.po.get_batt_to_grid()
        results_dict['year_one_wind_to_load_series'] = self.po.get_wind_to_load()
        results_dict['year_one_wind_to_battery_series'] = self.po.get_wind_to_batt()
        results_dict['year_one_wind_to_grid_series'] = self.po.get_wind_to_grid()

        self.results_dict = results_dict
        self.results_dict_bau = results_dict_bau
        self.path_templates = path_templates
        self.path_output = path_output
        self.path_static = os.path.join(path_static, self.file_proforma)
        self.path_proforma = os.path.join(path_output, self.file_proforma)
        self.year = year

        self.nested_outputs = self.setup_nested()
      

    def get_output(self):
        output_dict = {'flat':{}}
        for k in outputs().iterkeys():
            output_dict['flat'][k] = self.results_dict[k]
        self.get_nested()
        output_dict['nested'] = self.nested_outputs

        return output_dict

    def is_system(self):
        system = False
        if self.results_dict['pv_kw'] > 0 or self.results_dict['batt_kw'] > 0:
            system = True
        return system

    @staticmethod
    def setup_nested():

        # Add nested outputs (preserve original format for now to support backwards compatibility)
        nested_outputs = dict()
        nested_outputs["Scenario"] = dict()
        nested_outputs["Scenario"]["Site"] = dict()

        # Loop through all sub-site dicts and init
        for name, d in nested_output_definitions["Output"]["Scenario"]["Site"].items():
            nested_outputs["Scenario"]["Site"][name] = dict()
            for k in d.iterkeys():
                nested_outputs["Scenario"]["Site"][name].setdefault(k, None)

        return nested_outputs

    def get_nested(self):

        self.nested_outputs["Scenario"]["status"] = self.results_dict["status"]

        # format assumes that the flat format is still the primary default
        for name, d in nested_output_definitions["Output"]["Scenario"]["Site"].items():

            if name == "LoadProfile":
                self.nested_outputs["Scenario"]["Site"][name]["year_one_electric_load_series_kw"] = self.po.get_load_profile()
            elif name == "Financial":
                self.nested_outputs["Scenario"]["Site"][name]["lcc_us_dollars"] = self.results_dict["lcc"]
                self.nested_outputs["Scenario"]["Site"][name]["lcc_bau_us_dollars"] = self.results_dict["lcc_bau"]
                self.nested_outputs["Scenario"]["Site"][name]["npv_us_dollars"] = self.results_dict["npv"]
                self.nested_outputs["Scenario"]["Site"][name]["net_capital_costs_plus_om_us_dollars"] = self.results_dict["net_capital_costs_plus_om"]
            elif name == "PV":
                self.nested_outputs["Scenario"]["Site"][name]["size_kw"] = self.results_dict["pv_kw"]
                self.nested_outputs["Scenario"]["Site"][name]["average_yearly_energy_produced_kwh"] = self.results_dict["average_yearly_pv_energy_produced"]
                self.nested_outputs["Scenario"]["Site"][name]["average_yearly_energy_exported_kwh"] = self.results_dict["average_annual_energy_exported"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_produced_kwh"] = self.results_dict["year_one_energy_produced"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_power_production_series_kw"] = self.compute_total_power(name)
                self.nested_outputs["Scenario"]["Site"][name]["year_one_to_battery_series_kw"] = self.po.get_pv_to_batt()
                self.nested_outputs["Scenario"]["Site"][name]["year_one_to_load_series_kw"] = self.po.get_pv_to_load()
                self.nested_outputs["Scenario"]["Site"][name]["year_one_to_grid_series_kw"] = self.po.get_pv_to_grid()
            elif name == "Wind":
                self.nested_outputs["Scenario"]["Site"][name]["size_kw"] = self.results_dict["wind_kw"]
                self.nested_outputs["Scenario"]["Site"][name]["average_yearly_energy_produced_kwh"] = self.results_dict["average_wind_energy_produced"]
                self.nested_outputs["Scenario"]["Site"][name]["average_yearly_energy_exported_kwh"] = self.results_dict["average_annual_energy_exported_wind"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_produced_kwh"] = self.results_dict["year_one_wind_energy_produced"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_power_production_series_kw"] = self.compute_total_power(name)
                self.nested_outputs["Scenario"]["Site"][name]["year_one_to_battery_series_kw"] = self.po.get_wind_to_batt()
                self.nested_outputs["Scenario"]["Site"][name]["year_one_to_load_series_kw"] = self.po.get_wind_to_load()
                self.nested_outputs["Scenario"]["Site"][name]["year_one_to_grid_series_kw"] = self.po.get_wind_to_grid()
            elif name == "Storage":
                self.nested_outputs["Scenario"]["Site"][name]["size_kw"] = self.results_dict["batt_kw"]
                self.nested_outputs["Scenario"]["Site"][name]["size_kwh"] = self.results_dict["batt_kwh"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_to_load_series_kw"] = self.po.get_batt_to_load()
                self.nested_outputs["Scenario"]["Site"][name]["year_one_to_grid_series_kw"] = self.po.get_batt_to_grid()
                self.nested_outputs["Scenario"]["Site"][name]["year_one_soc_series_pct"] = self.po.get_soc(self.results_dict['batt_kwh'])
            elif name == "ElectricTariff":
                self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_cost_us_dollars"] = self.results_dict["year_one_energy_cost"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_demand_cost_us_dollars"] = self.results_dict["year_one_demand_cost"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_fixed_cost_us_dollars"] = self.results_dict["year_one_fixed_cost"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_min_charge_adder_us_dollars"] = self.results_dict["year_one_min_charge_adder"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_cost_bau_us_dollars"] = self.results_dict["year_one_energy_cost_bau"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_cost_us_dollars"] = self.results_dict["year_one_energy_cost"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_demand_cost_bau_us_dollars"] = self.results_dict["year_one_demand_cost_bau"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_fixed_cost_bau_us_dollars"] = self.results_dict["year_one_fixed_cost_bau"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_min_charge_adder_bau_us_dollars"] = self.results_dict["year_one_min_charge_adder_bau"]
                self.nested_outputs["Scenario"]["Site"][name]["total_energy_cost_us_dollars"] = self.results_dict["total_energy_cost"]
                self.nested_outputs["Scenario"]["Site"][name]["total_demand_cost_us_dollars"] = self.results_dict["total_demand_cost"]
                self.nested_outputs["Scenario"]["Site"][name]["total_fixed_cost_us_dollars"] = self.results_dict["total_fixed_cost"]
                self.nested_outputs["Scenario"]["Site"][name]["total_min_charge_adder_us_dollars"] = self.results_dict["total_min_charge_adder"]
                self.nested_outputs["Scenario"]["Site"][name]["total_energy_cost_bau_us_dollars"] = self.results_dict["total_energy_cost_bau"]
                self.nested_outputs["Scenario"]["Site"][name]["total_demand_cost_bau_us_dollars"] = self.results_dict["total_demand_cost_bau"]
                self.nested_outputs["Scenario"]["Site"][name]["total_fixed_cost_bau_us_dollars"] = self.results_dict["total_fixed_cost_bau"]
                self.nested_outputs["Scenario"]["Site"][name]["total_min_charge_adder_bau_us_dollars"] = self.results_dict["total_min_charge_adder_bau"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_bill_us_dollars"] = self.year_one_bill()
                self.nested_outputs["Scenario"]["Site"][name]["year_one_bill_bau_us_dollars"] = self.year_one_bill_bau()
                self.nested_outputs["Scenario"]["Site"][name]["year_one_export_benefit_us_dollars"] = self.results_dict["year_one_export_benefit"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_cost_series_us_dollars_per_kwh"] = self.po.get_energy_cost()
                self.nested_outputs["Scenario"]["Site"][name]["year_one_demand_cost_series_us_dollars_per_kw"] = self.po.get_demand_cost()
                self.nested_outputs["Scenario"]["Site"][name]["year_one_to_load_series_kw"] = self.po.get_grid_to_load()
                self.nested_outputs["Scenario"]["Site"][name]["year_one_to_battery_series_kw"] = self.po.get_grid_to_batt()
                self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_supplied_kwh"] = self.results_dict["year_one_utility_kwh"]

        """

        # Loop through all sub-site dicts and init
        for name, d in nested_output_definitions["Output"]["Scenario"]["Site"].items():
            # limit to financial, dispatch, and electric tariff outputs
            if "size_kw" not in d:
                if name == "ElectricTariff":
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_bill"] = self.year_one_bill()
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_bill_bau"] = self.year_one_bill_bau()

                for k in d.iterkeys():
                    if k in self.results_dict:
                        self.nested_outputs["Scenario"]["Site"][name][k] = self.results_dict[k]
                    elif k in self.results_dict_bau[k]:
                        self.nested_outputs["Scenario"]["Site"][name][k] = self.results_bau_dict[k]

            elif name == "PV":
                self.nested_outputs["Scenario"]["Site"][name]["size_kw"] = self.results_dict["pv_kw"]
                self.nested_outputs["Scenario"]["Site"][name]["average_yearly_energy_produced"] = self.results_dict["average_yearly_pv_energy_produced"]
                self.nested_outputs["Scenario"]["Site"][name]["average_yearly_energy_exported"] = self.results_dict["average_annual_energy_exported"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_produced"] = self.results_dict["year_one_energy_produced"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_power_production_series"] = self.compute_total_power(name)
            elif name == "Wind":
                self.nested_outputs["Scenario"]["Site"][name]["size_kw"] = self.results_dict["wind_kw"]
                self.nested_outputs["Scenario"]["Site"][name]["average_yearly_energy_produced"] = self.results_dict["average_wind_energy_produced"]
                self.nested_outputs["Scenario"]["Site"][name]["average_yearly_energy_exported"] = self.results_dict["average_annual_energy_exported_wind"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_produced"] = self.results_dict["year_one_wind_energy_produced"]
                self.nested_outputs["Scenario"]["Site"][name]["year_one_power_production_series"] = self.compute_total_power(name)
            elif name == "Storage":
                self.nested_outputs["Scenario"]["Site"][name]["size_kw"] = self.results_dict["batt_kw"]
                self.nested_outputs["Scenario"]["Site"][name]["size_kwh"] = self.results_dict["batt_kwh"]
            elif name == "Grid":
                self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_produced"] = self.results_dict["year_one_utility_kwh"]

        """

    def compute_total_power(self, tech):
        tech = tech.lower()
        power_lists = list()

        if self.results_dict["year_one_" + tech + "_to_load_series"] is not None:
            power_lists.append(self.results_dict["year_one_" + tech + "_to_load_series"])
        if self.results_dict["year_one_" + tech + "_to_battery_series"] is not None:
            power_lists.append(self.results_dict["year_one_" + tech + "_to_battery_series"])
        if self.results_dict["year_one_" + tech + "_to_grid_series"] is not None:
            power_lists.append(self.results_dict["year_one_" + tech + "_to_grid_series"])
        power = [sum(x) for x in zip(*power_lists)]
        return power

    def year_one_bill(self):
        return self.results_dict["year_one_demand_cost"] + self.results_dict["year_one_energy_cost"] + \
               self.results_dict["year_one_fixed_cost"] + self.results_dict["year_one_min_charge_adder"]

    def year_one_bill_bau(self):
        return self.results_dict["year_one_demand_cost_bau"] + self.results_dict["year_one_energy_cost_bau"] + \
               self.results_dict["year_one_fixed_cost_bau"] + self.results_dict["year_one_min_charge_adder_bau"]


