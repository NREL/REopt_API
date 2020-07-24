# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
import sys
import traceback
import copy
import numpy as np
from reo.nested_outputs import nested_output_definitions
import logging
from celery import shared_task, Task
from reo.exceptions import REoptError, UnexpectedError
from reo.models import ModelManager, PVModel, LoadProfileModel, ScenarioModel, LoadProfileBoilerFuelModel, \
    LoadProfileChillerElectricModel, ElectricChillerModel, BoilerModel
from reo.src.outage_costs import calc_avoided_outage_costs
from reo.src.profiler import Profiler
from reo.src.emissions_calculator import EmissionsCalculator
log = logging.getLogger(__name__)


class ProcessResultsTask(Task):
    """
    Used to define custom Error handling for celery task
    """
    name = 'process_results'
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

        self.request.chain = None  # stop the chain?
        self.request.callback = None
        self.request.chord = None  # this seems to stop the infinite chord_unlock call


@shared_task(bind=True, base=ProcessResultsTask, ignore_result=True)
def process_results(self, dfm_list, data, meta, saveToDB=True):
    """
    Processes the two outputs from reopt.jl bau and with-Tech scenarios
    :param self: celery.Task
    :param dfm_list: list of serialized dat_file_managers (passed from group of REopt runs)
    :param data: nested dict mirroring API response format
    :param meta: ={'run_uuid': run_uuid, 'api_version': api_version} from api.py
    :param saveToDB: boolean for saving postgres models
    :return: None
    """
    profiler = Profiler()

    class Results:

        bau_attributes = [
            "lcc",
            "fuel_used_gal",
            "year_one_energy_cost",
            "year_one_demand_cost",
            "year_one_fixed_cost",
            "year_one_min_charge_adder",
            "year_one_bill",
            "year_one_utility_kwh",
            "year_one_export_benefit",
            "GridToLoad",
            "total_energy_cost",
            "total_demand_cost",
            "total_fixed_cost",
            "total_min_charge_adder",
            "total_export_benefit",
            "net_capital_costs_plus_om",
            "gen_net_fixed_om_costs",
            "gen_net_variable_om_costs",
            "gen_total_fuel_cost",
            "gen_year_one_fuel_cost",
            "gen_year_one_variable_om_costs",
            "year_one_boiler_fuel_cost",
            "total_boiler_fuel_cost",
            "julia_input_construction_seconds",
            "julia_reopt_preamble_seconds",
            "julia_reopt_variables_seconds",
            "julia_reopt_constriants_seconds",
            "julia_reopt_optimize_seconds",
            "julia_reopt_postprocess_seconds",
            "pyjulia_start_seconds",
            "pyjulia_pkg_seconds",
            "pyjulia_activate_seconds",
            "pyjulia_include_model_seconds",
            "pyjulia_make_model_seconds",
            "pyjulia_include_reopt_seconds",
            "pyjulia_run_reopt_seconds"
        ]

        def __init__(self, results_dict, results_dict_bau, dm, inputs):
            """
            Convenience (and legacy) class for handling REopt results
            :param results_dict: flat dict of results from reopt.jl
            :param results_dict_bau: flat dict of results from reopt.jl for bau case
            :param instance of DataManager class
            :param dict, data['inputs']['Scenario']['Site']
            """
            self.dm = dm
            self.inputs = inputs

            # remove invalid sizes due to optimization error margins
            for r in [results_dict, results_dict_bau]:
                for key, value in r.items():
                    if key.endswith('kw') or key.endswith('kwh'):
                        if value < 0:
                            r[key] = 0

            # add bau outputs to results_dict
            for k in Results.bau_attributes:
                if results_dict_bau.get(k) is None:
                    results_dict[k + '_bau'] = 0
                else:
                    results_dict[k + '_bau'] = results_dict_bau[k]

            for i in range(len(self.inputs["PV"])):
                # b/c of PV & PVNM techs in REopt, if both are zero then no value is written to REopt_results.json
                i += 1
                if results_dict.get('PV{}_kw'.format(i)) is None:
                    results_dict['PV{}_kw'.format(i)] = 0
                pv_bau_keys = ["PV{}_net_fixed_om_costs".format(i),
                               "average_yearly_PV{}_energy_produced".format(i),
                               "year_one_PV{}_energy_produced".format(i),
                               "average_yearly_energy_produced_PV{}".format(i),
                              ]
                for k in pv_bau_keys:
                    if results_dict_bau.get(k) is None:
                        results_dict[k + '_bau'] = 0
                    else:
                        results_dict[k + '_bau'] = results_dict_bau[k]

            # if wind is zero then no value is written to REopt results.json
            if results_dict.get("wind_kw") is None:
                results_dict['wind_kw'] = 0

            # if generator is zero then no value is written to REopt results.json
            if results_dict.get("generator_kw") is None:
                results_dict['generator_kw'] = 0

            # if CHP is zero then no value is written to REopt results.json
            if results_dict.get("chp_kw") is None:
                results_dict['chp_kw'] = 0

            if results_dict.get("absorpchl_kw") is None:
                results_dict['absorpchl_kw'] = 0

            if results_dict.get("hot_tes_size_mmbtu") is None:
                results_dict['hot_tes_size_mmbtu'] = 0

            if results_dict.get("cold_tes_size_kwht") is None:
                results_dict['cold_tes_size_kwht'] = 0

            results_dict['npv'] = results_dict['lcc_bau'] - results_dict['lcc']

            self.results_dict = results_dict
            self.nested_outputs = self.setup_nested()

        @property
        def replacement_costs(self):
            replacement_costs = 0
            replacement_costs += self.inputs["Storage"]["replace_cost_us_dollars_per_kw"] * \
                                 self.nested_outputs["Scenario"]["Site"]["Storage"]["size_kw"]
            replacement_costs += self.inputs["Storage"]["replace_cost_us_dollars_per_kwh"] * \
                                 self.nested_outputs["Scenario"]["Site"]["Storage"]["size_kwh"]
            return round(replacement_costs, 2)

        @property
        def upfront_capex(self):
            upfront_capex = 0
            upfront_capex += max(self.inputs["Generator"]["installed_cost_us_dollars_per_kw"]
                                 * (self.nested_outputs["Scenario"]["Site"]["Generator"]["size_kw"]
                                 - self.inputs["Generator"]["existing_kw"]), 0)

            for pv in self.inputs["PV"]:
                upfront_capex += max(pv["installed_cost_us_dollars_per_kw"]
                                 * (self.nested_outputs["Scenario"]["Site"]["PV"][pv["pv_number"]-1]["size_kw"]
                                 - pv["existing_kw"]), 0)

            for tech in ["Storage", "Wind"]:
                upfront_capex += self.inputs[tech]["installed_cost_us_dollars_per_kw"] * \
                                 self.nested_outputs["Scenario"]["Site"][tech]["size_kw"]
            # storage capacity
            upfront_capex += self.inputs["Storage"]["installed_cost_us_dollars_per_kwh"] * \
                             self.nested_outputs["Scenario"]["Site"]["Storage"]["size_kwh"]

            return round(upfront_capex, 2)

        @property
        def upfront_capex_after_incentives(self):
            """
            The net_capital_costs output is the upfront capex after incentives, except it includes the battery
            replacement cost in present value. So we calculate the upfront_capex_after_incentives as net_capital_costs
            minus the battery replacement cost in present value
            """
            upfront_capex_after_incentives = self.nested_outputs["Scenario"]["Site"]["Financial"]["net_capital_costs"]

            pwf_inverter = 1 / ((1 + self.inputs["Financial"]["offtaker_discount_pct"])
                           **self.inputs["Storage"]["inverter_replacement_year"])

            pwf_storage = 1 / ((1 + self.inputs["Financial"]["offtaker_discount_pct"])
                          **self.inputs["Storage"]["battery_replacement_year"])

            inverter_future_cost = self.inputs["Storage"]["replace_cost_us_dollars_per_kw"] * \
                                   self.nested_outputs["Scenario"]["Site"]["Storage"]["size_kw"]

            storage_future_cost = self.inputs["Storage"]["replace_cost_us_dollars_per_kwh"] * \
                                  self.nested_outputs["Scenario"]["Site"]["Storage"]["size_kwh"]

            # NOTE these upfront costs include the tax benefit available to commercial entities
            upfront_capex_after_incentives -= inverter_future_cost * pwf_inverter * \
                                              (1 - self.inputs["Financial"]["offtaker_tax_pct"])
            upfront_capex_after_incentives -= storage_future_cost * pwf_storage * \
                                              (1 - self.inputs["Financial"]["offtaker_tax_pct"])
            return round(upfront_capex_after_incentives, 2)

        def get_output(self):
            self.get_nested()
            output_dict = self.nested_outputs
            return output_dict

        @staticmethod
        def setup_nested():
            """
            Set up up empty nested dict for outputs.
            :return: nested dict for outputs with values set to None. Results are filled in using "get_nested" method
            """
            nested_outputs = dict()
            nested_outputs["Scenario"] = dict()
            nested_outputs["Scenario"]["Profile"] = dict()
            nested_outputs["Scenario"]["Site"] = dict()

            # Loop through all sub-site dicts and init
            for name, d in nested_output_definitions["outputs"]["Scenario"]["Site"].items():
                nested_outputs["Scenario"]["Site"][name] = dict()
                for k in d.keys():
                    nested_outputs["Scenario"]["Site"][name].setdefault(k, None)
            return nested_outputs

        def get_nested(self):
            """
            Translates the "flat" results_dict (which is just the JSON output from REopt mosel code)
            into the nested output dict.
            :return: None (modifies self.nested_outputs)
            """
            # TODO: move the filling in of outputs to reopt.jl
            self.nested_outputs["Scenario"]["status"] = self.results_dict["status"]
            for name, d in nested_output_definitions["outputs"]["Scenario"]["Site"].items():
                if name == "LoadProfile":
                    self.nested_outputs["Scenario"]["Site"][name]["critical_load_series_kw"] = self.dm["LoadProfile"].get("critical_load_series_kw")
                    self.nested_outputs["Scenario"]["Site"][name]["annual_calculated_kwh"] = self.dm["LoadProfile"].get("annual_kwh")
                    self.nested_outputs["Scenario"]["Site"][name]["resilience_check_flag"] = self.dm["LoadProfile"].get("resilience_check_flag")
                    self.nested_outputs["Scenario"]["Site"][name]["sustain_hours"] = self.dm["LoadProfile"].get("sustain_hours")
                elif name == "LoadProfileBoilerFuel":
                    lpbf = LoadProfileBoilerFuelModel.objects.filter(run_uuid=meta['run_uuid'])[0]
                    self.nested_outputs["Scenario"]["Site"][name]["annual_calculated_boiler_fuel_load_mmbtu_bau"] = lpbf.annual_calculated_boiler_fuel_load_mmbtu_bau
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_boiler_fuel_load_series_mmbtu_per_hr"] = self.dm["LoadProfile"].get("year_one_boiler_fuel_load_series_mmbtu_per_hr")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_boiler_thermal_load_series_mmbtu_per_hr"] = [x * self.dm["boiler_efficiency"] for x in self.dm["LoadProfile"].get("year_one_boiler_fuel_load_series_mmbtu_per_hr")]
                elif name == "LoadProfileChillerElectric":
                    lpce = LoadProfileChillerElectricModel.objects.filter(run_uuid=meta['run_uuid'])[0]
                    self.nested_outputs["Scenario"]["Site"][name]["annual_calculated_kwh_bau"] = lpce.annual_calculated_kwh_bau
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_chiller_electric_load_series_kw"] = self.dm["LoadProfile"].get("year_one_chiller_electric_load_series_kw")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_chiller_thermal_load_series_ton"] = [x * self.dm["elecchl_cop"] / 3.5168545 for x in self.dm["LoadProfile"].get("year_one_chiller_electric_load_series_kw")]
                elif name == "Financial":
                    self.nested_outputs["Scenario"]["Site"][name]["lcc_us_dollars"] = self.results_dict.get("lcc")
                    self.nested_outputs["Scenario"]["Site"][name]["lcc_bau_us_dollars"] = self.results_dict.get(
                        "lcc_bau")
                    self.nested_outputs["Scenario"]["Site"][name]["npv_us_dollars"] = self.results_dict.get("npv")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "net_capital_costs_plus_om_us_dollars"] = self.results_dict.get("net_capital_costs_plus_om")
                    self.nested_outputs["Scenario"]["Site"][name]["net_capital_costs"] = self.results_dict.get(
                        "net_capital_costs")
                    self.nested_outputs["Scenario"]["Site"][name]["microgrid_upgrade_cost_us_dollars"] = \
                        self.results_dict.get("net_capital_costs") \
                        * data['inputs']['Scenario']['Site']['Financial']['microgrid_upgrade_cost_pct']
                    self.nested_outputs["Scenario"]["Site"][name]["total_opex_costs_us_dollars"] = self.results_dict.get(
                        "total_opex_costs")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_opex_costs_us_dollars"] = self.results_dict.get(
                        "year_one_opex_costs")
                elif name == "PV":
                    pv_models = list(PVModel.objects.filter(run_uuid=meta['run_uuid']).order_by('pv_number'))
                    template_pv = copy.deepcopy(self.nested_outputs['Scenario']["Site"][name])
                    self.nested_outputs['Scenario']["Site"][name] = []
                    for i, pv_model in enumerate(pv_models):
                        i += 1
                        pv = copy.deepcopy(template_pv)
                        pv["pv_number"] = i
                        pv["size_kw"] = self.results_dict.get("PV{}_kw".format(i)) or 0
                        pv["average_yearly_energy_produced_kwh"] = self.results_dict.get("average_yearly_energy_produced_PV{}".format(i))
                        pv["average_yearly_energy_produced_bau_kwh"] = self.results_dict.get("average_yearly_energy_produced_PV{}_bau".format(i))
                        pv["average_yearly_energy_exported_kwh"] = self.results_dict.get("average_annual_energy_exported_PV{}".format(i))
                        pv["year_one_energy_produced_kwh"] = self.results_dict.get("year_one_energy_produced_PV{}".format(i))
                        pv["year_one_to_battery_series_kw"] = self.results_dict.get("PV{}toBatt".format(i))
                        pv["year_one_to_load_series_kw"] = self.results_dict.get("PV{}toLoad".format(i))
                        pv["year_one_to_grid_series_kw"] = self.results_dict.get("PV{}toGrid".format(i))
                        pv["year_one_power_production_series_kw"] = pv.get("year_one_to_grid_series_kw")
                        if not pv.get("year_one_to_battery_series_kw") is None:
                            if pv["year_one_power_production_series_kw"] is None:
                                pv["year_one_power_production_series_kw"] = pv.get("year_one_to_battery_series_kw")
                            else:
                                pv["year_one_power_production_series_kw"]  = list(np.array(pv["year_one_power_production_series_kw"]) + np.array(pv.get("year_one_to_battery_series_kw")))
                        if not pv.get("year_one_to_load_series_kw") is None:
                            if pv["year_one_power_production_series_kw"] is None:
                                pv["year_one_power_production_series_kw"] = pv.get("year_one_to_load_series_kw")
                            else:
                                pv["year_one_power_production_series_kw"]  = list(np.array(pv["year_one_power_production_series_kw"]) + np.array(pv.get("year_one_to_load_series_kw")))                        
                        if pv["year_one_power_production_series_kw"] is None:
                            pv["year_one_power_production_series_kw"] = []
                        pv["existing_pv_om_cost_us_dollars"] = self.results_dict.get("PV{}_net_fixed_om_costs_bau".format(i))
                        pv["station_latitude"] = pv_model.station_latitude
                        pv["station_longitude"] = pv_model.station_longitude
                        pv["station_distance_km"] = pv_model.station_distance_km
                        self.nested_outputs['Scenario']["Site"][name].append(pv)
                elif name == "Wind":
                    self.nested_outputs["Scenario"]["Site"][name]["size_kw"] = self.results_dict.get("wind_kw", 0)
                    self.nested_outputs["Scenario"]["Site"][name][
                        "average_yearly_energy_produced_kwh"] = self.results_dict.get("average_wind_energy_produced")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "average_yearly_energy_exported_kwh"] = self.results_dict.get(
                        "average_annual_energy_exported_wind")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_energy_produced_kwh"] = self.results_dict.get("year_one_wind_energy_produced")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_battery_series_kw"] = self.results_dict.get("WINDtoBatt")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_load_series_kw"] = self.results_dict.get("WINDtoLoad")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_grid_series_kw"] = self.results_dict.get("WINDtoGrid")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_power_production_series_kw"] = self.compute_total_power(name)
                elif name == "Storage":
                    self.nested_outputs["Scenario"]["Site"][name]["size_kw"] = self.results_dict.get("batt_kw", 0)
                    self.nested_outputs["Scenario"]["Site"][name]["size_kwh"] = self.results_dict.get("batt_kwh", 0)
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_load_series_kw"] = self.results_dict.get("ElecFromStore")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_grid_series_kw"] = None
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_soc_series_pct"] = \
                        self.results_dict.get("year_one_soc_series_pct")
                elif name == "ElectricTariff":
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_energy_cost_us_dollars"] = self.results_dict.get("year_one_energy_cost")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_demand_cost_us_dollars"] = self.results_dict.get("year_one_demand_cost")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_fixed_cost_us_dollars"] = self.results_dict.get("year_one_fixed_cost")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_min_charge_adder_us_dollars"] = self.results_dict.get("year_one_min_charge_adder")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_energy_cost_bau_us_dollars"] = self.results_dict.get("year_one_energy_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_energy_cost_us_dollars"] = self.results_dict.get("year_one_energy_cost")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_demand_cost_bau_us_dollars"] = self.results_dict.get("year_one_demand_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_fixed_cost_bau_us_dollars"] = self.results_dict.get("year_one_fixed_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_min_charge_adder_bau_us_dollars"] = self.results_dict.get(
                        "year_one_min_charge_adder_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_energy_cost_us_dollars"] = self.results_dict.get("total_energy_cost")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_demand_cost_us_dollars"] = self.results_dict.get("total_demand_cost")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_fixed_cost_us_dollars"] = self.results_dict.get("total_fixed_cost")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_min_charge_adder_us_dollars"] = self.results_dict.get("total_min_charge_adder")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_energy_cost_bau_us_dollars"] = self.results_dict.get("total_energy_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_demand_cost_bau_us_dollars"] = self.results_dict.get("total_demand_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_fixed_cost_bau_us_dollars"] = self.results_dict.get("total_fixed_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_min_charge_adder_bau_us_dollars"] = self.results_dict.get("total_min_charge_adder_bau")
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_bill_us_dollars"] = self.results_dict.get(
                        "year_one_bill")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_bill_bau_us_dollars"] = self.results_dict.get("year_one_bill_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_export_benefit_us_dollars"] = self.results_dict.get("year_one_export_benefit")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_export_benefit_bau_us_dollars"] = self.results_dict.get("year_one_export_benefit_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_export_benefit_us_dollars"] = self.results_dict.get("total_export_benefit")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_export_benefit_bau_us_dollars"] = self.results_dict.get("total_export_benefit_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_energy_cost_series_us_dollars_per_kwh"] = \
                        self.dm.get('year_one_energy_cost_series_us_dollars_per_kwh')
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_demand_cost_series_us_dollars_per_kw"] = \
                        self.dm.get('year_one_demand_cost_series_us_dollars_per_kw')
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_load_series_kw"] = self.results_dict.get('GridToLoad')
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_load_bau_series_kw"] = self.results_dict.get('GridToLoad_bau')
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_battery_series_kw"] = self.results_dict.get('GridToBatt')
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_energy_supplied_kwh"] = self.results_dict.get("year_one_utility_kwh")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_energy_supplied_kwh_bau"] = self.results_dict.get("year_one_utility_kwh_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_chp_standby_cost_us_dollars"] = self.results_dict.get("year_one_chp_standby_cost")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_chp_standby_cost_us_dollars"] = self.results_dict.get("total_chp_standby_cost")
                elif name == "FuelTariff":
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_boiler_fuel_cost_us_dollars"] = self.results_dict.get("total_boiler_fuel_cost")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_boiler_fuel_cost_bau_us_dollars"] = self.results_dict.get("total_boiler_fuel_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_boiler_fuel_cost_us_dollars"] = self.results_dict.get("year_one_boiler_fuel_cost")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_boiler_fuel_cost_bau_us_dollars"] = self.results_dict.get("year_one_boiler_fuel_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_chp_fuel_cost_us_dollars"] = self.results_dict.get("total_chp_fuel_cost")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_chp_fuel_cost_us_dollars"] = self.results_dict.get("year_one_chp_fuel_cost")    
                elif name == "Generator":
                    self.nested_outputs["Scenario"]["Site"][name]["size_kw"] = self.results_dict.get("generator_kw", 0)
                    self.nested_outputs["Scenario"]["Site"][name]["fuel_used_gal"] = self.results_dict.get(
                        "fuel_used_gal")
                    self.nested_outputs["Scenario"]["Site"][name]["fuel_used_gal_bau"] = self.results_dict.get(
                        "fuel_used_gal_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_load_series_kw"] = self.results_dict.get('GENERATORtoLoad')
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_battery_series_kw"] = self.results_dict.get('GENERATORtoBatt')
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_grid_series_kw"] = self.results_dict.get('GENERATORtoGrid')
                    self.nested_outputs["Scenario"]["Site"][name][
                        "average_yearly_energy_produced_kwh"] = self.results_dict.get(
                        "average_yearly_gen_energy_produced")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "average_yearly_energy_exported_kwh"] = self.results_dict.get(
                        "average_annual_energy_exported_gen")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_energy_produced_kwh"] = self.results_dict.get(
                        "year_one_gen_energy_produced")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_power_production_series_kw"] = self.compute_total_power(name)
                    self.nested_outputs["Scenario"]["Site"][name][
                        "existing_gen_total_fixed_om_cost_us_dollars"] = self.results_dict.get(
                        "gen_net_fixed_om_costs_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_fixed_om_cost_us_dollars"] = self.results_dict.get("gen_net_fixed_om_costs")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_fixed_om_cost_us_dollars"] = self.results_dict.get("gen_year_one_fixed_om_costs")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "existing_gen_total_variable_om_cost_us_dollars"] = self.results_dict.get(
                        "gen_net_variable_om_costs_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "existing_gen_year_one_variable_om_cost_us_dollars"] = self.results_dict.get(
                        "gen_year_one_variable_om_costs_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_variable_om_cost_us_dollars"] = self.results_dict.get(
                        "gen_net_variable_om_costs")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_variable_om_cost_us_dollars"] = self.results_dict.get(
                        "gen_year_one_variable_om_costs")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "total_fuel_cost_us_dollars"] = self.results_dict.get(
                        "gen_total_fuel_cost")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_fuel_cost_us_dollars"] = self.results_dict.get(
                        "gen_year_one_fuel_cost")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "existing_gen_total_fuel_cost_us_dollars"] = self.results_dict.get(
                        "gen_total_fuel_cost_bau")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "existing_gen_year_one_fuel_cost_us_dollars"] = self.results_dict.get(
                        "gen_year_one_fuel_cost_bau")
                elif name == "CHP":
                    self.nested_outputs["Scenario"]["Site"][name][
                        "size_kw"] = self.results_dict.get("chp_kw")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_fuel_used_mmbtu"] = self.results_dict.get("year_one_chp_fuel_used")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_electric_energy_produced_kwh"] = self.results_dict.get("year_one_chp_electric_energy_produced")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_thermal_energy_produced_mmbtu"] = self.results_dict.get("year_one_chp_thermal_energy_produced")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_electric_production_series_kw"] = self.results_dict.get("chp_electric_production_series")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_battery_series_kw"] = self.results_dict.get("chp_to_battery_series")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_load_series_kw"] = self.results_dict.get("chp_electric_to_load_series")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_grid_series_kw"] = self.results_dict.get("chp_to_grid_series")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_thermal_to_load_series_mmbtu_per_hour"] = self.results_dict.get("chp_thermal_to_load_series")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_thermal_to_tes_series_mmbtu_per_hour"] = self.results_dict.get("chp_thermal_to_tes_series")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_thermal_to_waste_series_mmbtu_per_hour"] = self.results_dict.get("chp_thermal_to_waste_series")
                elif name == "Boiler":
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_boiler_fuel_consumption_series_mmbtu_per_hr"] = self.results_dict.get("fuel_to_boiler_series")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_boiler_thermal_production_series_mmbtu_per_hr"] = self.results_dict.get("boiler_thermal_production_series")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_thermal_to_load_series_mmbtu_per_hour"] = self.results_dict.get("boiler_thermal_to_load_series")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_thermal_to_tes_series_mmbtu_per_hour"] = self.results_dict.get("boiler_thermal_to_tes_series")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_boiler_fuel_consumption_mmbtu"] = self.results_dict.get("year_one_fuel_to_boiler_mmbtu")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_boiler_thermal_production_mmbtu"] = self.results_dict.get("year_one_boiler_thermal_production_mmbtu")
                elif name == "ElectricChiller":
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_electric_chiller_thermal_to_load_series_ton"] = [x / 3.51685 for x in self.results_dict.get("electric_chiller_to_load_series")]
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_electric_chiller_thermal_to_tes_series_ton"] =  [x / 3.51685 for x in self.results_dict.get("electric_chiller_to_tes_series")]
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_electric_chiller_electric_consumption_series_kw"] = self.results_dict.get("electric_chiller_consumption_series")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_electric_chiller_electric_consumption_kwh"] = self.results_dict.get("year_one_electric_chiller_electric_kwh")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_electric_chiller_thermal_production_tonhr"] = self.results_dict.get("year_one_electric_chiller_thermal_kwh") / 3.51685
                elif name == "AbsorptionChiller":
                    self.nested_outputs["Scenario"]["Site"][name][
                        "size_ton"] = self.results_dict.get("absorpchl_kw") / 3.51685
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_absorp_chl_thermal_to_load_series_ton"] = [x / 3.51685 for x in self.results_dict.get("absorption_chiller_to_load_series")]
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_absorp_chl_thermal_to_tes_series_ton"] = [x / 3.51685 for x in self.results_dict.get("absorption_chiller_to_tes_series")]
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_absorp_chl_thermal_consumption_series_mmbtu_per_hr"] = self.results_dict.get("absorption_chiller_consumption_series")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_absorp_chl_thermal_consumption_mmbtu"] = self.results_dict.get("year_one_absorp_chiller_thermal_consumption_mmbtu")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_absorp_chl_thermal_production_tonhr"] = self.results_dict.get("year_one_absorp_chiller_thermal_prod_kwh") / 3.51685
                elif name == "HotTES":
                    self.nested_outputs["Scenario"]["Site"][name][
                        "size_gal"] = self.results_dict.get("hot_tes_size_mmbtu",0) / 0.000163
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_thermal_from_hot_tes_series_mmbtu_per_hr"] = self.results_dict.get("hot_tes_thermal_production_series")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_hot_tes_soc_series_pct"] = self.results_dict.get("hot_tes_pct_soc_series")
                elif name == "ColdTES":
                    self.nested_outputs["Scenario"]["Site"][name][
                        "size_gal"] = self.results_dict.get("cold_tes_size_kwht",0) / 0.0287
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_thermal_from_cold_tes_series_ton"] = [x/3.51685 for x in self.results_dict.get("cold_tes_thermal_production_series")]
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_cold_tes_soc_series_pct"] = self.results_dict.get("cold_tes_pct_soc_series")

            # outputs that depend on multiple object results:
            self.nested_outputs["Scenario"]["Site"]["Financial"]["initial_capital_costs"] = self.upfront_capex
            self.nested_outputs["Scenario"]["Site"]["Financial"]["replacement_costs"] = self.replacement_costs
            self.nested_outputs["Scenario"]["Site"]["Financial"]["initial_capital_costs_after_incentives"] = \
                self.upfront_capex_after_incentives

            time_outputs = [k for k in self.bau_attributes if (k.startswith("julia") or k.startswith("pyjulia"))]

            for k in time_outputs:
                self.nested_outputs["Scenario"]["Profile"][k] = self.results_dict.get(k)
                self.nested_outputs["Scenario"]["Profile"][k + "_bau"] = self.results_dict.get(k + "_bau")

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
    self.user_uuid = data['outputs']['Scenario'].get('user_uuid')

    try:
        results_object = Results(results_dict=dfm_list[0]['results'], results_dict_bau=dfm_list[1]['results_bau'],
                                 dm=dfm_list[0], inputs=data['inputs']['Scenario']['Site'])
        results = results_object.get_output()
        
        # Move PV exported to grid during an outage to the curtailed PV series, doing this here so we have access to input data
        # Get outage start and end hour
        outage_start_hour= data['inputs']['Scenario']['Site']['LoadProfile'].get('outage_start_hour')
        outage_end_hour = data['inputs']['Scenario']['Site']['LoadProfile'].get('outage_end_hour')
        for pv in results['Scenario']['Site']['PV']:
            # If there is an outage move the PV exported to the grid to the curtailment series
            if len(pv["year_one_to_grid_series_kw"] or [])>0:
                pv['year_one_curtailed_production_series_kw'] = [0.0] * len(pv["year_one_to_grid_series_kw"])
                if (outage_start_hour is not None) and (outage_end_hour is not None):
                    outage_start_time_step = outage_start_hour * data['inputs']['Scenario']['time_steps_per_hour']
                    outage_end_time_step = outage_end_hour * data['inputs']['Scenario']['time_steps_per_hour']
                    pv['year_one_curtailed_production_series_kw'][outage_start_time_step : outage_end_time_step] = \
                        pv["year_one_to_grid_series_kw"][outage_start_time_step : outage_end_time_step]
                    pv["year_one_to_grid_series_kw"][outage_start_time_step : outage_end_time_step] = \
                        [0.0] * (outage_end_time_step - outage_start_time_step)

        data['outputs'].update(results)
        data['outputs']['Scenario'].update(meta)  # run_uuid and api_version

        pv_watts_station_check = data['outputs']['Scenario']['Site']['PV'][0].get('station_distance_km') or 0
        if pv_watts_station_check > 322:
            pv_warning = ("The best available solar resource data is {} miles from the site's coordinates. "
             "Consider choosing an alternative location closer to NREL's NSRDB or international datasets, shown "
             "at https://maps.nrel.gov/nsrdb-viewer/ and documented at https://nsrdb.nrel.gov/"
             ).format(round(pv_watts_station_check*0.621,0))
            
            if data.get('messages') is None:
                data['messages'] = {"PVWatts Warning": pv_warning}
            else:
                data['messages']["PVWatts Warning"] = pv_warning

        # Calculate avoided outage costs
        calc_avoided_outage_costs(data, present_worth_factor=dfm_list[0]['pwf_e'], run_uuid=self.run_uuid)

        data = EmissionsCalculator.add_to_data(data)
        if len(data['outputs']['Scenario']['Site']['PV']) == 1:
            data['outputs']['Scenario']['Site']['PV'] = data['outputs']['Scenario']['Site']['PV'][0]

        profiler.profileEnd()
        data['outputs']["Scenario"]["Profile"]["parse_run_outputs_seconds"] = profiler.getDuration()

        if saveToDB:
            ModelManager.update(data, run_uuid=self.run_uuid)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        log.info("Results.py raising the error: {}, detail: {}".format(exc_type, exc_value))
        raise UnexpectedError(exc_type, exc_value.args[0], traceback.format_tb(exc_traceback), task=self.name, run_uuid=self.run_uuid,
                              user_uuid=self.user_uuid)
