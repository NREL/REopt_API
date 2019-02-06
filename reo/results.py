from __future__ import absolute_import, unicode_literals
import os
import json
import sys
from reo.nested_outputs import nested_output_definitions
from reo.dispatch import ProcessOutputs
from reo.log_levels import log
from celery import shared_task, Task
from reo.exceptions import REoptError, UnexpectedError
from reo.models import ModelManager
from reo.src.outage_costs import calc_avoided_outage_costs
from reo.src.profiler import Profiler


class ResultsTask(Task):
    """
    Used to define custom Error handling for celery task
    """

    name = 'callback'
    max_retries = 0

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        log a bunch of stuff for debugging
        save message: error and outputs: Scenario: status
        need to stop rest of chain!?
        :param exc: The exception raised by the task.
        :param task_id: Unique id of the failed task. (not the run_uuid)
        :param args: Original arguments for the task that failed.
        :param kwargs: Original keyword arguments for the task that failed.
        :param einfo: ExceptionInfo instance, containing the traceback.

        :return: None, The return value of this handler is ignored.
        """
        if isinstance(exc, REoptError):
            exc.save_to_db()
        self.data["messages"]["error"] = exc.message
        self.data["outputs"]["Scenario"]["status"] = "An error occurred. See messages for more."
        ModelManager.update_scenario_and_messages(self.data, run_uuid=self.run_uuid)

        # self.request.chain = None  # stop the chain?
        # self.request.callback = None
        self.request.chord = None  # this seems to stop the infinite chord_unlock call


@shared_task(bind=True, base=ResultsTask, ignore_result=True)
def parse_run_outputs(self, dfm_list, data, meta, profiler, saveToDB=True):
    """
    Translates REopt_results.json into API outputs, along with time-series data saved to csv's by REopt.
    :param self: celery.Task
    :param dfm_list: list of serialized dat_file_managers (passed from group of REopt runs)
    :param data: nested dict mirroring API response format
    :param meta: ={'run_uuid': run_uuid, 'api_version': api_version} from api.py
    :param saveToDB: boolean for saving postgres models
    :return: None
    """
    profiler.profileStart('parse_run_outputs')

    paths = dfm_list[0]['paths']  # dfm_list = [dfm, dfm], one each from the two REopt jobs

    class Results:

        # file names
        file_proforma = 'ProForma.xlsm'
        file_dispatch = 'Dispatch.csv'

        bau_attributes = [
            "lcc",
            "year_one_energy_cost",
            "year_one_demand_cost",
            "year_one_fixed_cost",
            "year_one_min_charge_adder",
            "year_one_bill",
            "total_energy_cost",
            "total_demand_cost",
            "total_fixed_cost",
            "total_min_charge_adder",
            "net_capital_costs_plus_om"
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

            #remove invalid sizes due to optimization error margins
            for r in [results_dict,results_dict_bau]:
                for key,value in r.items():
                    if key.endswith('kw') or key.endswith('kwh'):
                        if value < 0:
                            r[key] = 0

            # add bau outputs to results_dict
            for k in Results.bau_attributes:
                results_dict[k+'_bau'] = results_dict_bau[k]

            # b/c of PV & PVNM techs in REopt, if both are zero then no value is written to REopt_results.json
            if results_dict.get('pv_kw') is None:
                results_dict['pv_kw'] = 0

            # if wind is zero then no value is written to REopt results.json
            if results_dict.get("wind_kw") is None:
                results_dict['wind_kw'] = 0


            results_dict['npv'] = results_dict['lcc_bau'] - results_dict['lcc']

            # dispatch
            self.po = ProcessOutputs(path_output, year)
            self.results_dict = results_dict
            self.results_dict_bau = results_dict_bau
            self.path_templates = path_templates
            self.path_output = path_output
            self.path_static = os.path.join(path_static, self.file_proforma)
            self.path_proforma = os.path.join(path_output, self.file_proforma)
            self.year = year

            self.nested_outputs = self.setup_nested()

        def get_output(self):
            self.get_nested()
            output_dict = self.nested_outputs

            return output_dict

        def is_system(self):
            system = False
            if self.results_dict['pv_kw'] > 0 or self.results_dict['batt_kw'] > 0:
                system = True
            return system

        @staticmethod
        def setup_nested():
            """
            Set up up empty nested dict for outputs.
            :return: nested dict for outputs with values set to None. Results are filled in using "get_nested" method
            """
            nested_outputs = dict()
            nested_outputs["Scenario"] = dict()
            nested_outputs["Scenario"]["Site"] = dict()

            # Loop through all sub-site dicts and init
            for name, d in nested_output_definitions["outputs"]["Scenario"]["Site"].items():
                nested_outputs["Scenario"]["Site"][name] = dict()
                for k in d.iterkeys():
                    nested_outputs["Scenario"]["Site"][name].setdefault(k, None)

            return nested_outputs

        def get_nested(self):
            """
            Translates the "flat" results_dict (which is just the JSON output from REopt mosel code)
            into the nested output dict.
            :return: None (modifies self.nested_outputs)
            """
            self.nested_outputs["Scenario"]["status"] = self.results_dict["status"]

            # format assumes that the flat format is still the primary default
            for name, d in nested_output_definitions["outputs"]["Scenario"]["Site"].items():

                if name == "LoadProfile":
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_electric_load_series_kw"] = self.po.get_load_profile()
                    self.nested_outputs["Scenario"]["Site"][name]["critical_load_series_kw"] = self.po.get_crit_load_profile()
                elif name == "Financial":
                    self.nested_outputs["Scenario"]["Site"][name]["lcc_us_dollars"] = self.results_dict.get("lcc")
                    self.nested_outputs["Scenario"]["Site"][name]["lcc_bau_us_dollars"] = self.results_dict.get("lcc_bau")
                    self.nested_outputs["Scenario"]["Site"][name]["npv_us_dollars"] = self.results_dict.get("npv")
                    self.nested_outputs["Scenario"]["Site"][name]["net_capital_costs_plus_om_us_dollars"] = self.results_dict.get("net_capital_costs_plus_om")
                    self.nested_outputs["Scenario"]["Site"][name]["net_capital_costs"] = self.results_dict.get("net_capital_costs")
                    self.nested_outputs["Scenario"]["Site"][name]["microgrid_upgrade_cost_us_dollars"] = \
                        self.results_dict.get("net_capital_costs") \
                        * data['inputs']['Scenario']['Site']['Financial']['microgrid_upgrade_cost_pct']
                elif name == "PV":
                    self.nested_outputs["Scenario"]["Site"][name]["size_kw"] = self.results_dict.get("pv_kw")
                    self.nested_outputs["Scenario"]["Site"][name]["average_yearly_energy_produced_kwh"] = self.results_dict.get("average_yearly_pv_energy_produced")
                    self.nested_outputs["Scenario"]["Site"][name]["average_yearly_energy_exported_kwh"] = self.results_dict.get("average_annual_energy_exported")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_produced_kwh"] = self.results_dict.get("year_one_energy_produced")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_to_battery_series_kw"] = self.po.get_pv_to_batt()
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_to_load_series_kw"] = self.po.get_pv_to_load()
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_to_grid_series_kw"] = self.po.get_pv_to_grid()
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_power_production_series_kw"] = self.compute_total_power(name)
                    self.nested_outputs["Scenario"]["Site"][name]["existing_pv_om_cost_us_dollars"] = self.results_dict.get("net_capital_costs_plus_om_bau")
                elif name == "Wind":
                    self.nested_outputs["Scenario"]["Site"][name]["size_kw"] = self.results_dict.get("wind_kw")
                    self.nested_outputs["Scenario"]["Site"][name]["average_yearly_energy_produced_kwh"] = self.results_dict.get("average_wind_energy_produced")
                    self.nested_outputs["Scenario"]["Site"][name]["average_yearly_energy_exported_kwh"] = self.results_dict.get("average_annual_energy_exported_wind")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_produced_kwh"] = self.results_dict.get("year_one_wind_energy_produced")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_to_battery_series_kw"] = self.po.get_wind_to_batt()
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_to_load_series_kw"] = self.po.get_wind_to_load()
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_to_grid_series_kw"] = self.po.get_wind_to_grid()
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_power_production_series_kw"] = self.compute_total_power(name)
                elif name == "Storage":
                    self.nested_outputs["Scenario"]["Site"][name]["size_kw"] = self.results_dict.get("batt_kw")
                    self.nested_outputs["Scenario"]["Site"][name]["size_kwh"] = self.results_dict.get("batt_kwh")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_to_load_series_kw"] = self.po.get_batt_to_load()
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_to_grid_series_kw"] = self.po.get_batt_to_grid()
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_soc_series_pct"] = self.po.get_soc(self.results_dict.get('batt_kwh'))
                elif name == "ElectricTariff":
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_cost_us_dollars"] = self.results_dict.get("year_one_energy_cost")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_demand_cost_us_dollars"] = self.results_dict.get("year_one_demand_cost")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_fixed_cost_us_dollars"] = self.results_dict.get("year_one_fixed_cost")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_min_charge_adder_us_dollars"] = self.results_dict.get("year_one_min_charge_adder")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_cost_bau_us_dollars"] = self.results_dict.get("year_one_energy_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_cost_us_dollars"] = self.results_dict.get("year_one_energy_cost")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_demand_cost_bau_us_dollars"] = self.results_dict.get("year_one_demand_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_fixed_cost_bau_us_dollars"] = self.results_dict.get("year_one_fixed_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_min_charge_adder_bau_us_dollars"] = self.results_dict.get("year_one_min_charge_adder_bau")
                    self.nested_outputs["Scenario"]["Site"][name]["total_energy_cost_us_dollars"] = self.results_dict.get("total_energy_cost")
                    self.nested_outputs["Scenario"]["Site"][name]["total_demand_cost_us_dollars"] = self.results_dict.get("total_demand_cost")
                    self.nested_outputs["Scenario"]["Site"][name]["total_fixed_cost_us_dollars"] = self.results_dict.get("total_fixed_cost")
                    self.nested_outputs["Scenario"]["Site"][name]["total_min_charge_adder_us_dollars"] = self.results_dict.get("total_min_charge_adder")
                    self.nested_outputs["Scenario"]["Site"][name]["total_energy_cost_bau_us_dollars"] = self.results_dict.get("total_energy_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name]["total_demand_cost_bau_us_dollars"] = self.results_dict.get("total_demand_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name]["total_fixed_cost_bau_us_dollars"] = self.results_dict.get("total_fixed_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name]["total_min_charge_adder_bau_us_dollars"] = self.results_dict.get("total_min_charge_adder_bau")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_bill_us_dollars"] = self.results_dict.get("year_one_bill")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_bill_bau_us_dollars"] = self.results_dict.get("year_one_bill_bau")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_export_benefit_us_dollars"] = self.results_dict.get("year_one_export_benefit")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_cost_series_us_dollars_per_kwh"] = self.po.get_energy_cost()
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_demand_cost_series_us_dollars_per_kw"] = self.po.get_demand_cost()
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_to_load_series_kw"] = self.po.get_grid_to_load()
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_to_battery_series_kw"] = self.po.get_grid_to_batt()
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_energy_supplied_kwh"] = self.results_dict.get("year_one_utility_kwh")
                elif name == "Generator":
                    self.nested_outputs["Scenario"]["Site"][name]["fuel_used_gal"] = self.results_dict.get("fuel_used_gal")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_to_load_series_kw"] = self.po.get_gen_to_load()

        def compute_total_power(self, tech):
            power_lists = list()
            d = self.nested_outputs["Scenario"]["Site"][tech]

            if d.get("year_one_to_load_series_kw") is not None:
                power_lists.append(d["year_one_to_load_series_kw"])

            if d.get("year_one_to_battery_series_kw") is not None:
                power_lists.append(d["year_one_to_battery_series_kw"])

            if d.get("year_one_to_grid_series_kw") is not None:
                power_lists.append(d["year_one_to_grid_series_kw"])

            power = [sum(x) for x in zip(*power_lists)]
            return power

    self.data = data
    self.run_uuid = data['outputs']['Scenario']['run_uuid']

    try:
        year = data['inputs']['Scenario']['Site']['LoadProfile']['year']
        output_file = os.path.join(paths['outputs'], "REopt_results.json")

        if not os.path.exists(output_file):
            msg = "Optimization failed to run. Output file does not exist: " + output_file
            log.debug("Current directory: " + os.getcwd())
            log.error(msg)
            raise RuntimeError('REopt', msg)

        process_results = Results(paths['templates'], paths['outputs'], paths['outputs_bau'],
                                  paths['static_outputs'], year)
        results = process_results.get_output()

        data['outputs'].update(results)
        data['outputs']['Scenario'].update(meta)  # run_uuid and api_version

        # Calculate avoided outage costs
        calc_avoided_outage_costs(data, present_worth_factor=dfm_list[0]['pwf_e'])

        if saveToDB:
            ModelManager.update(data, run_uuid=self.run_uuid)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        log("Results.py raise unexpected error")
        raise UnexpectedError(exc_type, exc_value, exc_traceback, task=self.name, run_uuid=self.run_uuid)

    profiler.profileEnd('parse_run_outputs')
