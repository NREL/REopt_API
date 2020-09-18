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
from reo.models import ModelManager, PVModel, FinancialModel, WindModel
from reo.src.outage_costs import calc_avoided_outage_costs
from reo.src.profiler import Profiler
from reo.src.emissions_calculator import EmissionsCalculator
from reo.utilities import annuity, degradation_factor
from proforma.models import ProForma
from reo.nested_inputs import macrs_five_year, macrs_seven_year
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

def calculate_simple_payback_and_irr(data):
        """
        Recreates the ProForma spreadsheet calculations to get the simple payback period
        :param data: dict a complete response from the REopt API for a successfully completed job
        :return: float, the simple payback of the system, if the system recuperates its costs
        """
            
        #Sort out the inputs and outputs by model so that all needed data is in consolidated locations
        electric_tariff = copy.deepcopy(data['outputs']['Scenario']['Site']['ElectricTariff'])
        electric_tariff.update(data['inputs']['Scenario']['Site']['ElectricTariff'])
        financials =  copy.deepcopy(data['outputs']['Scenario']['Site']['Financial'])
        financials.update(data['inputs']['Scenario']['Site']['Financial'])
        pvs =  copy.deepcopy(data['outputs']['Scenario']['Site']['PV'])
        if type(pvs) == dict:
           pvs = [pvs] 
        in_pvs = copy.deepcopy(data['inputs']['Scenario']['Site']['PV'])
        if type(data['inputs']['Scenario']['Site']['PV']) == dict:
            in_pvs = [in_pvs]
        for i, pv in enumerate(in_pvs):
            pvs[i].update(pv)
        wind =  copy.deepcopy(data['outputs']['Scenario']['Site']['Wind'])
        wind.update(data['inputs']['Scenario']['Site']['Wind'])
        storage =  copy.deepcopy(data['outputs']['Scenario']['Site']['Storage'])
        storage.update(data['inputs']['Scenario']['Site']['Storage'])
        generator =  copy.deepcopy(data['outputs']['Scenario']['Site']['Generator'])
        generator.update(data['inputs']['Scenario']['Site']['Generator'])
        years = financials['analysis_years']
        two_party = financials['two_party_ownership']
        
        #Create placeholder variables to store summed totals across all relevant techs
        federal_itc = 0
        om_series = np.array([0.0 for _ in range(years)])
        om_series_bau = np.array([0.0 for _ in range(years)])
        total_pbi = np.array([0.0 for _ in range(years)])
        total_pbi_bau = np.array([0.0 for _ in range(years)])
        total_depreciation = np.array([0.0 for _ in range(years)])
        total_ibi_and_cbi = 0
        
        #calculate PV capital costs, o+m costs, incentives, and depreciation
        for pv in pvs:
            new_kw = (pv.get('size_kw') or 0) - (pv.get('existing_kw') or 0)
            total_kw = pv.get('size_kw') or 0
            existing_kw = pv.get('existing_kw') or 0
            #existing PV is considered free
            capital_costs = new_kw * pv['installed_cost_us_dollars_per_kw'] 
            #assume owner is responsible for both new and existing PV maintenance in optimal case
            if two_party:
                annual_om = -1 * new_kw * pv['om_cost_us_dollars_per_kw'] 
            else:
                annual_om = -1 * total_kw * pv['om_cost_us_dollars_per_kw'] 
            annual_om_bau = -1 * existing_kw * pv['om_cost_us_dollars_per_kw']
            om_series += np.array([annual_om * (1+financials['om_cost_escalation_pct'])**yr for yr in range(1, years+1)])
            om_series_bau += np.array([annual_om_bau * (1+financials['om_cost_escalation_pct'])**yr for yr in range(1, years+1)])
            #incentive calculations, in the spreadsheet utility incentives are applied first
            utility_ibi = min(capital_costs * pv['utility_ibi_pct'], pv['utility_ibi_max_us_dollars'])
            utility_cbi = min(new_kw * pv['utility_rebate_us_dollars_per_kw'], pv['utility_rebate_max_us_dollars'])
            state_ibi = min((capital_costs - utility_ibi - utility_cbi) * pv['state_ibi_pct'], pv['state_ibi_max_us_dollars'])
            state_cbi = min(new_kw * pv['state_rebate_us_dollars_per_kw'], pv['state_rebate_max_us_dollars'])
            federal_cbi = new_kw * pv['federal_rebate_us_dollars_per_kw']
            ibi = utility_ibi + state_ibi 
            cbi = utility_cbi + federal_cbi + state_cbi
            total_ibi_and_cbi += (ibi + cbi)
            
            pbi_series = np.array([])
            pbi_series_bau = np.array([])
            existing_energy_bau = (pv.get('year_one_energy_produced_bau_kwh') or 0) if two_party else 0
            # Production-based incentives
            for yr in range(years):
                if yr < pv['pbi_years']:
                    degredation_pct = (1- (pv['degradation_pct']))**yr
                    base_pbi = min(pv['pbi_us_dollars_per_kwh'] * ((pv['year_one_energy_produced_kwh'] or 0) - existing_energy_bau) *\
                         degredation_pct,  pv['pbi_max_us_dollars'] * degredation_pct )
                    base_pbi_bau = min(pv['pbi_us_dollars_per_kwh'] * (pv.get('year_one_energy_produced_bau_kwh') or 0) *\
                         degredation_pct,  pv['pbi_max_us_dollars'] * degredation_pct )
                    pbi_series = np.append(pbi_series, base_pbi)
                    pbi_series_bau = np.append(pbi_series_bau, base_pbi_bau)
                else:
                    pbi_series = np.append(pbi_series, 0.0)
                    pbi_series_bau = np.append(pbi_series_bau, 0.0)
            total_pbi += pbi_series
            total_pbi_bau += pbi_series_bau
            # Depreciation
            if pv['macrs_option_years'] in [5,7]:
                if pv['macrs_option_years'] == 5:
                    schedule = macrs_five_year
                if pv['macrs_option_years'] == 7:
                    schedule = macrs_seven_year
                federal_itc_basis = capital_costs - state_ibi - utility_ibi - state_cbi - utility_cbi - federal_cbi
                federal_itc_amount = pv['federal_itc_pct'] * federal_itc_basis
                federal_itc += federal_itc_amount
                macrs_bonus_basis = federal_itc_basis - (federal_itc_basis * pv['federal_itc_pct'] * pv['macrs_itc_reduction'])
                macrs_basis = macrs_bonus_basis * (1 - pv['macrs_bonus_pct'])
                depreciation_schedule = np.array([0.0 for _ in range(years)])
                for i,r in enumerate(schedule):
                    depreciation_schedule[i] = macrs_basis * r
                depreciation_schedule[0] += (pv['macrs_bonus_pct'] * macrs_bonus_basis)
                total_depreciation += depreciation_schedule

        #calculate Wind capital costs, o+m costs, incentives, and depreciation
        if (wind['size_kw'] or 0) > 0:
            total_kw = wind.get('size_kw') or 0
            capital_costs = total_kw * wind['installed_cost_us_dollars_per_kw']        
            annual_om = -1 * total_kw * wind['om_cost_us_dollars_per_kw']
            om_series += np.array([annual_om * (1+financials['om_cost_escalation_pct'])**yr for yr in range(1, years+1)])
            utility_ibi = min(capital_costs * wind['utility_ibi_pct'], wind['utility_ibi_max_us_dollars'])
            utility_cbi = min(total_kw * wind['utility_rebate_us_dollars_per_kw'], wind['utility_rebate_max_us_dollars'])
            state_ibi = min((capital_costs - utility_ibi - utility_cbi) * wind['state_ibi_pct'], wind['state_ibi_max_us_dollars'])
            state_cbi = min(total_kw * wind['state_rebate_us_dollars_per_kw'], wind['state_rebate_max_us_dollars'])
            federal_cbi = total_kw * wind['federal_rebate_us_dollars_per_kw']
            ibi = utility_ibi + state_ibi 
            cbi = utility_cbi + federal_cbi + state_cbi
            total_ibi_and_cbi += (ibi + cbi)
            # Production-based incentives
            pbi_series = np.array([])
            for yr in range(years):
                if yr < wind['pbi_years']:
                    base_pbi = min(wind['pbi_us_dollars_per_kwh'] * (wind['year_one_energy_produced_kwh'] or 0), \
                      wind['pbi_max_us_dollars'])
                    pbi_series = np.append(pbi_series, base_pbi)
                else:
                    pbi_series = np.append(pbi_series, 0.0)
            total_pbi += pbi_series
            # Depreciation
            if wind['macrs_option_years'] in [5,7]:
                if wind['macrs_option_years'] == 5:
                    schedule = macrs_five_year
                if wind['macrs_option_years'] == 7:
                    schedule = macrs_seven_year
                federal_itc_basis = capital_costs - state_ibi - utility_ibi - state_cbi - utility_cbi - federal_cbi
                federal_itc_amount = wind['federal_itc_pct']*federal_itc_basis
                federal_itc += federal_itc_amount
                macrs_bonus_basis = federal_itc_basis - (federal_itc_basis * wind['federal_itc_pct'] * wind['macrs_itc_reduction'])
                macrs_basis = macrs_bonus_basis * (1 - wind['macrs_bonus_pct'])
                depreciation_schedule = np.array([0.0 for _ in range(years)])
                for i,r in enumerate(schedule):
                    depreciation_schedule[i] = macrs_basis * r
                depreciation_schedule[0] += (wind['macrs_bonus_pct'] * macrs_bonus_basis)
                total_depreciation += depreciation_schedule

        #calculate Storage capital costs, o+m costs, incentives, and depreciation
        if (storage['size_kw'] or 0) > 0:
            total_kw = storage.get('size_kw') or 0
            total_kwh = storage.get('size_kwh') or 0
            capital_costs = (total_kw * storage['installed_cost_us_dollars_per_kw']) + (total_kwh * storage['installed_cost_us_dollars_per_kwh'])
            battery_replacement_year = int(storage['battery_replacement_year'])
            battery_replacement_cost = -1 * ((total_kw * storage['replace_cost_us_dollars_per_kw']) + (total_kwh * storage['replace_cost_us_dollars_per_kwh']))
            om_series += np.array([0 if yr != battery_replacement_year else battery_replacement_cost for yr in range(1, years+1)])
            
            #storage only has cbi in the API
            cbi = (total_kw * storage['total_rebate_us_dollars_per_kw']) + (total_kwh * (storage.get('total_rebate_us_dollars_per_kw') or 0)) 
            total_ibi_and_cbi += (cbi)
            # Depreciation
            if storage['macrs_option_years'] in [5,7]:
                if storage['macrs_option_years'] == 5:
                    schedule = macrs_five_year
                if storage['macrs_option_years'] == 7:
                    schedule = macrs_seven_year
                federal_itc_basis = capital_costs - cbi
                federal_itc_amount = storage['total_itc_pct']*federal_itc_basis
                federal_itc += federal_itc_amount
                macrs_bonus_basis = federal_itc_basis - (federal_itc_basis * storage['total_itc_pct'] * storage['macrs_itc_reduction'])
                macrs_basis = macrs_bonus_basis * (1 - storage['macrs_bonus_pct'])
                depreciation_schedule = np.array([0.0 for _ in range(years)])
                for i,r in enumerate(schedule):
                    depreciation_schedule[i] = macrs_basis * r
                depreciation_schedule[0] += (storage['macrs_bonus_pct'] * macrs_bonus_basis)
                total_depreciation += depreciation_schedule

        #calculate Generator capital costs, o+m costs, incentives, and depreciation
        if (generator['size_kw'] or 0) > 0:
            total_kw = generator.get('size_kw') or 0
            new_kw = (generator.get('size_kw') or 0) - (generator.get('existing_kw') or 0)
            existing_kw = generator.get('existing_kw') or 0
            
            # In the two party case the developer does not include the fuel cost in their costs
            # It is assumed that the offtaker will pay for this at a rate that is not marked up
            # to cover developer profits
            if not two_party:
                annual_om = -1 * ((total_kw * generator['om_cost_us_dollars_per_kw']) + \
                    (generator['year_one_variable_om_cost_us_dollars']) + 
                    (generator['year_one_fuel_cost_us_dollars']))
                
                annual_om_bau = -1 * ((existing_kw * generator['om_cost_us_dollars_per_kw']) + \
                    (generator['existing_gen_year_one_variable_om_cost_us_dollars']) + 
                    (generator['existing_gen_year_one_fuel_cost_us_dollars']))
            else:
                annual_om = -1 * ((total_kw * generator['om_cost_us_dollars_per_kw']) + \
                    (generator['year_one_variable_om_cost_us_dollars']))
                
                annual_om_bau = -1 * ((existing_kw * generator['om_cost_us_dollars_per_kw']) + \
                    (generator['existing_gen_year_one_variable_om_cost_us_dollars']))
            
            om_series += np.array([annual_om * (1+financials['om_cost_escalation_pct'])**yr for yr in range(1, years+1)])                
            om_series_bau += np.array([annual_om_bau * (1+financials['om_cost_escalation_pct'])**yr for yr in range(1, years+1)])
        
        #Optimal Case calculations
        electricity_bill_series = np.array([-1 * electric_tariff['year_one_bill_us_dollars'] * \
                                (1+financials['escalation_pct'])**yr for yr in range(1, years+1)])
        export_credit_series = np.array([-1 * electric_tariff['year_one_export_benefit_us_dollars'] * \
                                (1+financials['escalation_pct'])**yr for yr in range(1, years+1)])
        
        # In the two party case the electricity and export credits are incurred by the offtaker not the developer
        if two_party:
            total_operating_expenses = om_series
        else:
            total_operating_expenses = electricity_bill_series + export_credit_series + om_series

        # Set tax rate based off ownership type
        if two_party:
            tax_pct = financials['owner_tax_pct']
        else:
            tax_pct = financials['offtaker_tax_pct']

        # Apply taxes to operating expenses
        if tax_pct  > 0:
            deductable_operating_expenses_series = copy.deepcopy(total_operating_expenses) 
        else:
            deductable_operating_expenses_series = np.array([0]*years)

        operating_expenses_after_tax = deductable_operating_expenses_series * (1 - tax_pct)
        total_cash_incentives = total_pbi * (1 - tax_pct) 
        total_depreciation = total_depreciation * tax_pct
        free_cashflow_before_income = total_depreciation + total_cash_incentives + operating_expenses_after_tax
        free_cashflow_before_income[0] += federal_itc
        free_cashflow_before_income = np.append([(-1 * financials['initial_capital_costs']) + total_ibi_and_cbi], free_cashflow_before_income)
        
        if two_party:
            # get cumulative cashflow for developer
            discounted_cashflow = [v/((1+financials['owner_discount_pct'])**yr) for yr, v in enumerate(free_cashflow_before_income)]
            capital_recovery_factor = (financials['owner_discount_pct'] * (1+financials['owner_discount_pct'])**years) / \
                                        ((1+financials['owner_discount_pct'])**years - 1) / (1 - tax_pct)
            annual_income_from_host = -1 * sum(discounted_cashflow) * capital_recovery_factor * (1-tax_pct)
            free_cashflow = copy.deepcopy(free_cashflow_before_income)
            free_cashflow[1:] += annual_income_from_host
            irr = np.irr(free_cashflow)
            cumulative_cashflow =  np.cumsum(free_cashflow)
        else:
            # get cumulative cashflow for host by comparing to BAU cashflow
            electricity_bill_bau_series_bau = np.array([-1 * electric_tariff['year_one_bill_bau_us_dollars'] * \
                                    (1+financials['escalation_pct'])**yr for yr in range(1, years+1)])
            export_credit_bau_series_bau = np.array([electric_tariff['total_export_benefit_bau_us_dollars'] * \
                                    (1+financials['escalation_pct'])**yr for yr in range(1, years+1)])
            total_operating_expenses_bau = electricity_bill_bau_series_bau + export_credit_bau_series_bau + om_series_bau
            total_cash_incentives_bau = total_pbi_bau * (1 - financials['offtaker_tax_pct']) 
            if financials['offtaker_tax_pct'] > 0:
                deductable_operating_expenses_series_bau = copy.deepcopy(total_operating_expenses_bau) 
            else:
                deductable_operating_expenses_series_bau = np.array([0]*years)
            operating_expenses_after_tax_bau = deductable_operating_expenses_series_bau * (1 - financials['offtaker_tax_pct'])
            free_cashflow_before_income_bau = operating_expenses_after_tax_bau + total_cash_incentives_bau
            free_cashflow_before_income_bau = np.append([0], free_cashflow_before_income_bau)
            # difference optimal and BAU
            free_cashflow =  free_cashflow_before_income - free_cashflow_before_income_bau                                          
            irr = np.irr(free_cashflow)
            cumulative_cashflow =  np.cumsum(free_cashflow)
        
        #when the cumulative cashflow goes positive, scale the amount by the free cashflow to 
        #approximate a partial year
        if cumulative_cashflow[-1] < 0:
            return None, None
            
        simple_payback_years = 0
        for i in range(1, years+1):
            # add years where the cumulative cashflow is negative
            if cumulative_cashflow[i] < 0: 
                simple_payback_years += 1
            # fractionally add years where the cumulative cashflow became positive
            elif (cumulative_cashflow[i-1] < 0) and (cumulative_cashflow[i] > 0): 
                simple_payback_years += -(cumulative_cashflow[i-1]/free_cashflow[i])
            # skip years where cumulative cashflow is positive and the previous year's is too
        
        return round(simple_payback_years,4), round(irr,4)

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
            "GridToLoad",
            "year_one_energy_cost",
            "year_one_demand_cost",
            "year_one_fixed_cost",
            "year_one_min_charge_adder",
            "year_one_bill",
            "year_one_utility_kwh",
            "year_one_export_benefit",
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
            "pyjulia_run_reopt_seconds",
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

        def calculate_lcoe(self, tech_results_dict, tech_inputs_dict, financials):
            """
            The LCOE is calculated as annualized costs (capital and O+M translated to current value) divided by annualized energy
            output
            :param tech_results_dict: dict of model results (i.e. outputs from PVModel )
            :param tech_inputs_dict: dict of model results (i.e. inputs to PVModel )
            :param financials: financial model storing input financial parameters
            :return: float, LCOE in US dollars per kWh
            """
            years = financials.analysis_years # length of financial life

            if financials.two_party_ownership:
                discount_pct = financials.owner_discount_pct
                federal_tax_pct = financials.owner_tax_pct
            else:
                discount_pct = financials.offtaker_discount_pct
                federal_tax_pct = financials.offtaker_tax_pct

            new_kw = (tech_results_dict.get('size_kw') or 0) - (tech_inputs_dict.get('existing_kw') or 0) # new capacity
            
            if new_kw == 0:
                return None

            capital_costs = new_kw * tech_inputs_dict['installed_cost_us_dollars_per_kw'] # pre-incentive capital costs
            
            annual_om = new_kw * tech_inputs_dict['om_cost_us_dollars_per_kw'] # NPV of O&M charges escalated over financial life
            
            om_series = [annual_om * (1+financials.om_cost_escalation_pct)**yr for yr in range(1, years+1)]
            npv_om = sum([om * (1.0/(1.0+discount_pct))**yr for yr, om in enumerate(om_series,1)])
            
            #Incentives as calculated in the spreadsheet, note utility incentives are applied before state incentives
            utility_ibi = min(capital_costs * tech_inputs_dict['utility_ibi_pct'], tech_inputs_dict['utility_ibi_max_us_dollars'])
            utility_cbi = min(new_kw * tech_inputs_dict['utility_rebate_us_dollars_per_kw'], tech_inputs_dict['utility_rebate_max_us_dollars'])
            state_ibi = min((capital_costs - utility_ibi - utility_cbi) * tech_inputs_dict['state_ibi_pct'], tech_inputs_dict['state_ibi_max_us_dollars'])
            state_cbi = min(new_kw * tech_inputs_dict['state_rebate_us_dollars_per_kw'], tech_inputs_dict['state_rebate_max_us_dollars'])
            federal_cbi = new_kw * tech_inputs_dict['federal_rebate_us_dollars_per_kw']
            ibi = utility_ibi + state_ibi  #total investment-based incentives
            cbi = utility_cbi + federal_cbi + state_cbi #total capacity-based incentives
 
            #calculate energy in the BAU case, used twice later on
            if 'year_one_energy_produced_bau_kwh' in tech_results_dict.keys():
                existing_energy_bau = tech_results_dict['year_one_energy_produced_bau_kwh'] or 0
            else:
                existing_energy_bau = 0
            
            #calculate the value of the production-based incentive stream
            npv_pbi = 0 
            if tech_inputs_dict['pbi_max_us_dollars'] > 0:
                for yr in range(years):
                    if yr < tech_inputs_dict['pbi_years']:
                        degredation_pct = (1- (tech_inputs_dict.get('degradation_pct') or 0))**yr
                        base_pbi = min(tech_inputs_dict['pbi_us_dollars_per_kwh'] * \
                            ((tech_results_dict['year_one_energy_produced_kwh'] or 0) - existing_energy_bau) * \
                             degredation_pct,  tech_inputs_dict['pbi_max_us_dollars'] * degredation_pct )
                        base_pbi = base_pbi * (1.0/(1.0+discount_pct))**(yr+1)
                        npv_pbi += base_pbi
    
            npv_federal_itc = 0
            depreciation_schedule = np.array([0.0 for _ in range(years)])
            if tech_inputs_dict['macrs_option_years'] in [5,7]:
                if tech_inputs_dict['macrs_option_years'] == 5:
                    schedule = macrs_five_year
                if tech_inputs_dict['macrs_option_years'] == 7:
                    schedule = macrs_seven_year
                federal_itc_basis = capital_costs - state_ibi - utility_ibi - state_cbi - utility_cbi - federal_cbi
                federal_itc_amount = tech_inputs_dict['federal_itc_pct'] * federal_itc_basis
                npv_federal_itc = federal_itc_amount * (1.0/(1.0+discount_pct)) 
                macrs_bonus_basis = federal_itc_basis - (federal_itc_basis * tech_inputs_dict['federal_itc_pct'] * tech_inputs_dict['macrs_itc_reduction'])
                macrs_basis = macrs_bonus_basis * (1 - tech_inputs_dict['macrs_bonus_pct'])
                for i,r in enumerate(schedule):
                    depreciation_schedule[i] = macrs_basis * r
                depreciation_schedule[0] += (tech_inputs_dict['macrs_bonus_pct'] * macrs_bonus_basis)

            tax_deductions = (np.array(om_series)  + np.array(depreciation_schedule)) * federal_tax_pct
            npv_tax_deductions = sum([i* (1.0/(1.0+discount_pct))**yr for yr,i in enumerate(tax_deductions,1)])

            #we only care about the energy produced by new capacity in LCOE calcs
            annual_energy = (tech_results_dict['year_one_energy_produced_kwh'] or 0) - existing_energy_bau
            npv_annual_energy = sum([annual_energy * ((1.0/(1.0+discount_pct))**yr) * \
                (1- (tech_inputs_dict.get('degradation_pct') or 0))**(yr-1) for yr, i in enumerate(tax_deductions,1)])
            
            #LCOE is calculated as annualized costs divided by annualized energy
            lcoe = (capital_costs + npv_om - npv_pbi - cbi - ibi - npv_federal_itc - npv_tax_deductions ) / \
                    (npv_annual_energy)
            
            return round(lcoe,4)

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
            financials = FinancialModel.objects.filter(run_uuid=meta['run_uuid']).first() #getting financial inputs for wind and pv lcoe calculations
            for name, d in nested_output_definitions["outputs"]["Scenario"]["Site"].items():
                if name == "LoadProfile":
                    self.nested_outputs["Scenario"]["Site"][name]["year_one_electric_load_series_kw"] = self.dm["LoadProfile"].get("year_one_electric_load_series_kw")
                    self.nested_outputs["Scenario"]["Site"][name]["critical_load_series_kw"] = self.dm["LoadProfile"].get("critical_load_series_kw")
                    self.nested_outputs["Scenario"]["Site"][name]["annual_calculated_kwh"] = self.dm["LoadProfile"].get("annual_kwh")
                    self.nested_outputs["Scenario"]["Site"][name]["resilience_check_flag"] = self.dm["LoadProfile"].get("resilience_check_flag")
                    self.nested_outputs["Scenario"]["Site"][name]["sustain_hours"] = self.dm["LoadProfile"].get("sustain_hours")
                    self.nested_outputs["Scenario"]["Site"][name]['loads_kw'] = self.dm["LoadProfile"].get("loads_kw")
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
                        pv["year_one_energy_produced_bau_kwh"] = self.results_dict.get("year_one_PV{}_energy_produced_bau".format(i))
                        pv["year_one_to_battery_series_kw"] = self.results_dict.get("PV{}toBatt".format(i))
                        pv["year_one_to_load_series_kw"] = self.results_dict.get("PV{}toLoad".format(i))
                        pv["year_one_to_grid_series_kw"] = self.results_dict.get("PV{}toGrid".format(i))
                        pv['year_one_curtailed_production_series_kw'] = self.results_dict.get("PV{}toCurtail".format(i))
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
                        pv['lcoe_us_dollars_per_kwh'] = self.calculate_lcoe(pv, pv_model.__dict__, financials)
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
                        "year_one_curtailed_production_series_kw"] = self.results_dict.get("WINDtoCurtail")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_power_production_series_kw"] = self.compute_total_power(name)
                    if self.nested_outputs["Scenario"]["Site"][name]["size_kw"] > 0: #setting up
                        wind_model = WindModel.objects.get(run_uuid=meta['run_uuid'])
                        self.nested_outputs["Scenario"]["Site"][name]['lcoe_us_dollars_per_kwh'] = self.calculate_lcoe(self.nested_outputs["Scenario"]["Site"][name], wind_model.__dict__, financials)
                        data['inputs']['Scenario']["Site"]["Wind"]["installed_cost_us_dollars_per_kw"] = wind_model.installed_cost_us_dollars_per_kw
                        data['inputs']['Scenario']["Site"]["Wind"]["federal_itc_pct"] = wind_model.federal_itc_pct
                    else:
                        self.nested_outputs["Scenario"]["Site"][name]['lcoe_us_dollars_per_kwh'] = None
                elif name == "Storage":
                    self.nested_outputs["Scenario"]["Site"][name]["size_kw"] = self.results_dict.get("batt_kw", 0)
                    self.nested_outputs["Scenario"]["Site"][name]["size_kwh"] = self.results_dict.get("batt_kwh", 0)
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_load_series_kw"] = self.results_dict.get("ElecFromBatt")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_grid_series_kw"] = self.results_dict.get("ElecFromBattExport")
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
                        "year_one_to_load_series_bau_kw"] = self.results_dict.get('GridToLoad_bau')
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_to_battery_series_kw"] = self.results_dict.get('GridToBatt')
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_energy_supplied_kwh"] = self.results_dict.get("year_one_utility_kwh")
                    self.nested_outputs["Scenario"]["Site"][name][
                        "year_one_energy_supplied_kwh_bau"] = self.results_dict.get("year_one_utility_kwh_bau")
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
        
        data['outputs'].update(results)
        data['outputs']['Scenario'].update(meta)  # run_uuid and api_version
        
        #simple payback needs all data to be computed so running that calculation here
        simple_payback, irr = calculate_simple_payback_and_irr(data)  
        data['outputs']['Scenario']['Site']['Financial']['simple_payback_years'] = simple_payback
        data['outputs']['Scenario']['Site']['Financial']['irr_pct'] = irr if not np.isnan(irr or np.nan) else None
        data = EmissionsCalculator.add_to_data(data)

        pv_watts_station_check = data['outputs']['Scenario']['Site']['PV'][0].get('station_distance_km') or 0
        if pv_watts_station_check > 322:
            pv_warning = ("The best available solar resource data is {} miles from the site's coordinates."
                " Beyond 200 miles, we display this warning. Consider choosing an alternative location closer"
                " to the continental US with similar solar irradiance and weather patterns and rerunning the analysis."
                " For more information, see https://maps.nrel.gov/nsrdb-viewer/ and the documenation at https://nsrdb.nrel.gov/"
             ).format(round(pv_watts_station_check*0.621,0))
            
            if data.get('messages') is None:
                data['messages'] = {"PVWatts Warning": pv_warning}
            else:
                data['messages']["PVWatts Warning"] = pv_warning

        # Calculate avoided outage costs
        #calc_avoided_outage_costs(data, present_worth_factor=dfm_list[0]['pwf_e'], run_uuid=self.run_uuid)

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
