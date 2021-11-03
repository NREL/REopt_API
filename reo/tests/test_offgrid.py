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
import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class TestOffGridSystem(ResourceTestCaseMixin, TestCase):
    """
    Test off-grid analyses
    """

    def setUp(self):
        super(TestOffGridSystem, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'

        self.post = {
              "Scenario": {
                "off_grid_flag": True,
                "optimality_tolerance_techs": 0.05,
                "Site": {
                  "latitude": 34.5794343,
                  "longitude": -118.11646129999997,
                  "address": "Palmdale CA",
                  "land_acres": 10000,
                  "roof_squarefeet": 0.0,
                  "Financial": {
                    "om_cost_escalation_pct": 0.025,
                    # "escalation_pct": 0.023,
                    "generator_fuel_escalation_pct": 0.027,
                    "offtaker_tax_pct": 0.26,
                    "offtaker_discount_pct": 0.083,
                    #"owner_discount_pct":0.083,
                    "analysis_years": 25,
                    # "microgrid_upgrade_cost_pct": 0.0,
                    "other_capital_costs_us_dollars": 50000,
                    "other_annual_costs_us_dollars_per_year": 4000,
                    "third_party_ownership": False,
                  },
                  "LoadProfile": {
                    "doe_reference_name": "RetailStore",
                    "annual_kwh": 87600.0,
                    "year": 2017,
                    "outage_start_time_step": 1, # This should get overwritten to be 1 
                    "outage_end_time_step": 8760,
                    ## "critical_load_pct": 0.05, # This returns an error if not set to 1.0
                    # "outage_is_major_event": False,
                    "min_load_met_pct": 0.9999, # 0.9999, # 1.0, # 0.98
                    "sr_required_pct": 0.1
                  },
                  "PV": {
                    "existing_kw": 0.0,
                    "min_kw": 0.0,
                    "max_kw": 1.0e5,
                    "sr_required_pct": 0.25,
                    # "installed_cost_us_dollars_per_kw": 1600.0,
                    # "om_cost_us_dollars_per_kw": 16.0,
                    # "macrs_option_years": 0,
                    # "macrs_bonus_pct": 0,
                    # "macrs_itc_reduction": 0,
                    # "federal_itc_pct": 0,
                    # "state_ibi_pct": 0.0,
                    # "state_ibi_max_us_dollars": 0.0,
                    # "utility_ibi_pct": 0.0,
                    # "utility_ibi_max_us_dollars": 0.0,
                    # "federal_rebate_us_dollars_per_kw": 0.0,
                    # "state_rebate_us_dollars_per_kw": 0.0,
                    # "state_rebate_max_us_dollars": 0.0,
                    # "utility_rebate_us_dollars_per_kw": 0.0,
                    # "utility_rebate_max_us_dollars": 0.0,
                    # "pbi_us_dollars_per_kwh": 0.0,
                    # "pbi_max_us_dollars": 0.0,
                    # "pbi_years": 1.0,
                    # "pbi_system_max_kw": 0.0,
                    # "degradation_pct": 0.005,
                    # "azimuth": 180.0,
                    # "losses": 0.14,
                    # "array_type": 0,
                    # "module_type": 0,
                    # "gcr": 0.4,
                    # "dc_ac_ratio": 1.2,
                    # "inv_eff": 0.96,
                    # "radius": 0.0,
                    # "tilt": 34.5794343,
                    # "location": "ground"
                  },
                  "Storage": {
                    "min_kw": 0.0,
                    "max_kw": 1000.0,
                    "min_kwh": 0.0,
                    "max_kwh": 1000.0,
                    # "internal_efficiency_pct": 0.975,
                    # "inverter_efficiency_pct": 0.96,
                    # "rectifier_efficiency_pct": 0.96,
                    # "soc_min_pct": 0.2,
                    # "soc_init_pct": 1.0,
                    # "canGridCharge": False,
                    # "installed_cost_us_dollars_per_kw": 840.0,
                    # "installed_cost_us_dollars_per_kwh": 420.0,
                    # "replace_cost_us_dollars_per_kw": 410.0,
                    # "replace_cost_us_dollars_per_kwh": 200.0,
                    # "inverter_replacement_year": 10,
                    # "battery_replacement_year": 7,
                    # "macrs_option_years": 0,
                    # "macrs_bonus_pct": 0,
                    # "macrs_itc_reduction": 0,
                    # "total_itc_pct": 0.0,
                    # "total_rebate_us_dollars_per_kw": 0
                  },
                  "Generator": {
                    "useful_life_years": 5,
                    "existing_kw": 0.0,
                    "min_kw": 0.0,
                    "max_kw": 10000.0, # 100.0,
                    "installed_cost_us_dollars_per_kw": 500.0,
                    "om_cost_us_dollars_per_kw": 10.0,
                    "om_cost_us_dollars_per_kwh": 0.0,
                    "diesel_fuel_cost_us_dollars_per_gallon": 3.0,
                    # "fuel_slope_gal_per_kwh": 0.1,
                    # "fuel_intercept_gal_per_hr": 0.023,
                    # "fuel_avail_gal": 1000000000,
                    "min_turn_down_pct": 0.15,
                    # "generator_only_runs_during_grid_outage": True,
                    # "generator_sells_energy_back_to_grid": False,
                    # "macrs_option_years": 0,
                    # "macrs_bonus_pct": 0.0,
                    # "macrs_itc_reduction": 0.0,
                    # "federal_itc_pct": 0.0,
                    # "state_ibi_pct": 0.0,
                    # "state_ibi_max_us_dollars": 0.0,
                    # "utility_ibi_pct": 0.0,
                    # "utility_ibi_max_us_dollars": 0.0,
                    # "federal_rebate_us_dollars_per_kw": 0.0,
                    # "state_rebate_us_dollars_per_kw": 0.0,
                    # "state_rebate_max_us_dollars": 0.0,
                    # "utility_rebate_us_dollars_per_kw": 0.0,
                    # "utility_rebate_max_us_dollars": 0.0,
                    # "pbi_us_dollars_per_kwh": 0.0,
                    # "pbi_max_us_dollars": 0.0,
                    # "pbi_years": 0.0,
                    # "pbi_system_max_kw": 0.0
                  }
                },
                "user_uuid": None,
                "description": "",
                "time_steps_per_hour": 1, # 2, # 
                "webtool_uuid": None
              }
            }

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        uuid = json.loads(initial_post.content)['run_uuid']
        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
        return response

    def test_off_grid_modeling(self):
        response = self.get_response(self.post)
        pv_out = response['outputs']['Scenario']['Site']['PV']
        messages = response['messages']
        outputs = response['outputs']['Scenario']['Site']
        inputs = response['inputs']['Scenario']['Site']

        try:
            print('LCOE [$/kWh]: ', outputs['Financial']['microgrid_lcoe_us_dollars_per_kwh'])
            print('\nLCOE Breakdown:')
            print('Fuel:', outputs["Financial"]["lcoe_component_fuel_us_dollars_per_kwh"])
            print('RE Capex:', outputs["Financial"]["lcoe_component_re_capex_us_dollars_per_kwh"])
            print('Generator Capex:', outputs["Financial"]["lcoe_component_diesel_capex_us_dollars_per_kwh"])
            print('O&M:', outputs["Financial"]["lcoe_component_om_us_dollars_per_kwh"])
            print('Other Capex:', outputs["Financial"]["lcoe_component_other_capex_us_dollars_per_kwh"])
            print('Other Annual Costs:', outputs["Financial"]["lcoe_component_other_annual_costs_us_dollars_per_kwh"])

            print('\nPV size [kW]: ', outputs['PV']['size_kw'])
            print('Battery size [kWh]: ', outputs['Storage']['size_kwh'])
            print('Battery size [kW]: ', outputs['Storage']['size_kw'])
            print('Generator size [kW]:', outputs['Generator']['size_kw'])

            print('\nnet_capital_costs:', outputs['Financial']["net_capital_costs"])

            print('Load SR required (summed over year):', sum(outputs['LoadProfile']['total_sr_required']))
            print('Load SR provided (summed over year):', sum(outputs['LoadProfile']['total_sr_provided']))

            # Load Met constraint: 
            print('Input Min Load Met [%]: ', inputs['LoadProfile']["min_load_met_pct"])
            print('Load met [kWh]: ', sum(outputs['LoadProfile']["load_met_series_kw"]))
            print('Load [kWh]: ', sum(outputs['LoadProfile']["year_one_electric_load_series_kw"]) )
            # print('Output Load met, calculated [%]: ', sum(outputs['LoadProfile']["load_met_series_kw"]) / sum(outputs['LoadProfile']["year_one_electric_load_series_kw"]) )
            print('Output Load met, in nested_outputs [%]: ', outputs['LoadProfile']["load_met_pct"])


            # print('year_one_to_load_series_kw', response['outputs']['Scenario']['Site']['PV']['year_one_to_load_series_kw'])

            # Check outage start and end time step, critical load %, outage is major event
            self.assertEqual(inputs["LoadProfile"]["outage_start_time_step"], 1,
                             "outage_start_time_step does not equal 1. Equals {}".format(inputs["LoadProfile"]["outage_start_time_step"]))
            # self.assertEqual(inputs["LoadProfile"]["outage_end_time_step"], 8760,
            #                  "outage_end_time_step does not equal 8760. Equals {}".format(inputs["LoadProfile"]["outage_end_time_step"]))
            self.assertEqual(inputs["LoadProfile"]["critical_load_pct"], 1.0,
                             "Critical load pct does not equal 1. Equals {}".format(inputs["LoadProfile"]["critical_load_pct"]))    
            self.assertEqual(inputs["Generator"]["generator_sells_energy_back_to_grid"], False,
                             "generator_sells_energy_back_to_grid is not False. Equals {}".format(inputs["Generator"]["generator_sells_energy_back_to_grid"])) 
            self.assertEqual(inputs["LoadProfile"]["outage_is_major_event"], False,
                             "outage_is_major_event is not False. Equals {}".format(inputs["LoadProfile"]["outage_is_major_event"])) 

            # Check for no interaction with grid
            self.assertEqual(sum(outputs["Generator"]["year_one_to_grid_series_kw"]), 0.0,
                             "Generator sum(year_one_to_grid_series_kw) does not equal 0. Equals {}".format(sum(outputs["Generator"]["year_one_to_grid_series_kw"])))
            self.assertEqual(sum(outputs["PV"]["year_one_to_grid_series_kw"]), 0.0,
                             "PV sum(year_one_to_grid_series_kw) does not equal 0. Equals {}".format(sum(outputs["PV"]["year_one_to_grid_series_kw"])))
            self.assertEqual(sum(outputs["Storage"]["year_one_to_grid_series_kw"]), 0.0,
                             "Storage sum(year_one_to_grid_series_kw) does not equal 0. Equals {}".format(sum(outputs["Storage"]["year_one_to_grid_series_kw"])))

            # Check that Load met % is greater than requirement
            self.assertGreaterEqual(outputs["LoadProfile"]["load_met_pct"],
                                    inputs['LoadProfile']["min_load_met_pct"],
                                    "Load met pct is less than required pct.")
                      
            # TODO: check that lcoe components add up to 100%  

            ## path = 'reo/tests/data/outputs/'
            ## json.dump(response, open(path+'/'+"offgrid_results.json", "w"))

            # output_df = pd.DataFrame()
            # output_df['load'] = response['outputs']['Scenario']['Site']['LoadProfile']['year_one_electric_load_series_kw']
            # output_df['load_met'] = response['outputs']['Scenario']['Site']['LoadProfile']['load_met_series_kw']
            # output_df['load_sr_required'] = response['outputs']['Scenario']['Site']['LoadProfile']['sr_required_series_kw']
            # output_df['batt_sr_provided'] = response['outputs']['Scenario']['Site']['Storage']['sr_provided_series_kw']

            # output_df['pv_tot'] = response['outputs']['Scenario']['Site']['PV']['year_one_power_production_series_kw']
            # output_df['pv_1R'] = response['outputs']['Scenario']['Site']['PV']['year_one_to_load_series_kw']
            # output_df['pv_1S'] = response['outputs']['Scenario']['Site']['PV']['year_one_to_battery_series_kw']
            # output_df['pv_grid'] = response['outputs']['Scenario']['Site']['PV']['year_one_to_grid_series_kw']
            # output_df['pv_curtailed'] = response['outputs']['Scenario']['Site']['PV']['year_one_curtailed_production_series_kw']
            # output_df['pv_sr_required'] = response['outputs']['Scenario']['Site']['PV']['sr_required_series_kw']
            # output_df['pv_sr_provided'] = response['outputs']['Scenario']['Site']['PV']['sr_provided_series_kw']
            # output_df['gen_1R'] = response['outputs']['Scenario']['Site']['Generator']['year_one_to_load_series_kw']
            # output_df['gen_1S'] = response['outputs']['Scenario']['Site']['Generator']['year_one_to_battery_series_kw']
            # output_df['gen_grid'] = response['outputs']['Scenario']['Site']['Generator']['year_one_to_grid_series_kw']
            # output_df['gen_sr_provided'] = response['outputs']['Scenario']['Site']['Generator']['sr_provided_series_kw']

            # output_df['total_sr_required'] = response['outputs']['Scenario']['Site']['LoadProfile']['total_sr_required']
            # output_df['total_sr_provided'] = response['outputs']['Scenario']['Site']['LoadProfile']['total_sr_provided']

            ## output_df.to_csv('reo/tests/data/outputs/test_load_constraints.csv')

            # self.assertEqual(pv_out['size_kw'], expected_pv_size,
            #                  "AC size ({}) does not equal expected AC size ({})."
            #                  .format(pv_out['size_kw'], expected_pv_size))
        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("test_flex_tech API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e
