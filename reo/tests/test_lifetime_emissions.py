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
import pandas as pd
import os

class ClassAttributes:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)


class TestEmissions(ResourceTestCaseMixin, TestCase):
    """
    Test lifecycle climate and health emissions calculations
    """

    def setUp(self):
        super(TestEmissions, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'

        self.post_no_techs = {
          "Scenario": {
            "time_steps_per_hour": 1,
            "include_climate_in_objective": True,
            "include_health_in_objective": True,
            "Site": {
              "longitude": -93.2650,
              "latitude": 44.9778,
              "roof_squarefeet": None,
              "land_acres": None,
              "PV": {
                "max_kw": 0.0,
                "min_kw": 0.0,
              },
              "Generator": {
                "max_kw": 0.0,
                "min_kw": 0.0,
                "existing_kw": 0.0,
              },
              "LoadProfile": {
                "critical_loads_kw_is_net": False,
                "year": 2020,
                "loads_kw_is_net": True,
                "outage_start_time_step": None,
                "outage_end_time_step": None,
                "doe_reference_name": "FlatLoad",
                "annual_kwh": 8760.0
              },
              "Storage": {
                "max_kwh": 0.0,
                "min_kw": 0.0,
                "max_kw": 0.0,
                "min_kwh": 0.0,
              },
              "ElectricTariff": {
                ## "emissions_factor_series_lb_CO2_per_kwh": [1.0],
                "add_blended_rates_to_urdb_rate": False,
                "wholesale_rate_us_dollars_per_kwh": 0.0,
                "net_metering_limit_kw": 0.0,
                "interconnection_limit_kw": 100000000.0,
                "urdb_utility_name": "",
                "urdb_label": "",
                "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0,
                "urdb_rate_name": "custom",
                "urdb_response": None,
                "blended_monthly_rates_us_dollars_per_kwh": [0.15, 0.2, 0.21, 0.23, 0.27, 0.19, 0.22, 0.17, 0.24, 0.26, 0.18, 0.2],
                "blended_monthly_demand_charges_us_dollars_per_kw": [0.08, 0.11, 0, 0, 0.15, 0.14, 0.09, 0.06, 0, 0, 0.05, 0]
              },
              "Financial": {
                "escalation_pct": 0.026,
                "offtaker_discount_pct": 0.081,
                "value_of_lost_load_us_dollars_per_kwh": 100.0,
                "analysis_years": 20,
                "microgrid_upgrade_cost_pct": 0.3,
                "offtaker_tax_pct": 0.26,
                "om_cost_escalation_pct": 0.025,
                "co2_cost_us_dollars_per_tonne": 51.0,
                "nox_cost_us_dollars_per_tonne_grid": 51.0, # TODO: change to values from EASIUR! (and also make seasonal?)
                "so2_cost_us_dollars_per_tonne_grid": 51.0, # TODO: change to values from EASIUR! 
                "pm25_cost_us_dollars_per_tonne_grid": 51.0, # TODO: change to values from EASIUR! 
                "nox_cost_us_dollars_per_tonne_onsite_fuelburn": 51.0, # TODO: change to values from EASIUR! (and also make seasonal?)
                "so2_cost_us_dollars_per_tonne_onsite_fuelburn": 51.0, # TODO: change to values from EASIUR! 
                "pm25_cost_us_dollars_per_tonne_onsite_fuelburn": 51.0 # TODO: change to values from EASIUR! 
              },
              "Wind": {
                "max_kw": 0.0,
                "min_kw": 0.0
              }
            }
          }
        }

        self.post_with_techs = {
          "Scenario": {
            "time_steps_per_hour": 1,
            "include_climate_in_objective": True,
            "include_health_in_objective": True,
            "Site": {
              "longitude": -97.7431, # Austin TX
              "latitude": 30.2672,
              "roof_squarefeet": None,
              "land_acres": None,
              "PV": {
                "min_kw": 0.0,
                "max_kw": 1.0e9,
              },
              "Generator": {
                "existing_kw": 0.0,
                "min_kw": 0.0,
                "max_kw": 1.0e9,
              },
              "Storage": {
                "min_kw": 0.0,
                "max_kw": 1.0e9,
                "min_kwh": 0.0,
                "max_kwh": 1000000.0,  
              },
              "LoadProfile": {
                "critical_loads_kw_is_net": False,
                "year": 2020,
                "loads_kw_is_net": True,
                "outage_start_time_step": None,
                "outage_end_time_step": None,
                "doe_reference_name": "FlatLoad",
                "annual_kwh": 8760.0
              },
              "ElectricTariff": {
                # "emissions_factor_series_lb_CO2_per_kwh": [1.0],
                "emissions_factor_CO2_pct_decrease": 0.01174, 
                "add_blended_rates_to_urdb_rate": False,
                "wholesale_rate_us_dollars_per_kwh": 0.0,
                "net_metering_limit_kw": 0.0,
                "interconnection_limit_kw": 100000000.0,
                "urdb_utility_name": "",
                "urdb_label": "",
                "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0,
                "urdb_rate_name": "custom",
                "urdb_response": None,
                "blended_monthly_rates_us_dollars_per_kwh": [0.15, 0.2, 0.21, 0.23, 0.27, 0.19, 0.22, 0.17, 0.24, 0.26, 0.18, 0.2],
                "blended_monthly_demand_charges_us_dollars_per_kw": [0.08, 0.11, 0, 0, 0.15, 0.14, 0.09, 0.06, 0, 0, 0.05, 0]
              },
              "Financial": {
                "escalation_pct": 0.026,
                "offtaker_discount_pct": 0.083,
                "value_of_lost_load_us_dollars_per_kwh": 0.0,
                "analysis_years": 25,
                "microgrid_upgrade_cost_pct": 0.0,
                "offtaker_tax_pct": 0.26,
                "om_cost_escalation_pct": 0.025,
                "co2_cost_us_dollars_per_tonne": 51.0,
                "co2_cost_escalation_pct": 0.017173, 
                # "nox_cost_escalation_pct": , 
                # "nox_cost_us_dollars_per_tonne_grid": 0.0, 
                # "so2_cost_us_dollars_per_tonne_grid": 0.0, 
                # "pm25_cost_us_dollars_per_tonne_grid": 0.0, 
                # "nox_cost_us_dollars_per_tonne_onsite_fuelburn": 0.0, 
                # "so2_cost_us_dollars_per_tonne_onsite_fuelburn": 0.0, 
                # "pm25_cost_us_dollars_per_tonne_onsite_fuelburn": 0.0  
              },
            }
          }
        }

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        
        uuid = json.loads(initial_post.content)['run_uuid']
        print(uuid)

        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
        
        return response
    

    def test_emissions_modeling(self):

        response = self.get_response(self.post_with_techs)
        inputs = response['inputs']['Scenario']['Site']
        outputs = response['outputs']['Scenario']['Site']
        
        pv_out = response['outputs']['Scenario']['Site']['PV']
        messages = response['messages']

        try:
            print('Emissions Region: ', response['outputs']['Scenario']['Site']['ElectricTariff']['emissions_region'])
            print('PV size: ', response['outputs']['Scenario']['Site']['PV']['size_kw'])
            print('Batt kWh: ', response['outputs']['Scenario']['Site']['Storage']['size_kwh'])
            print('Batt kW: ', response['outputs']['Scenario']['Site']['Storage']['size_kw'])
            print('Generator kW: ', response['outputs']['Scenario']['Site']['Generator']['size_kw'])
            print('Annual Load kWh: ', response['outputs']['Scenario']['Site']["LoadProfile"]["annual_calculated_kwh"])
            print('Year 1 kWh from grid: ', response['outputs']['Scenario']['Site']["ElectricTariff"]["year_one_energy_supplied_kwh"])
            print('Year 1 kWh from grid BAU: ', response['outputs']['Scenario']['Site']["ElectricTariff"]["year_one_energy_supplied_kwh_bau"])

            print('Generator fuel use (gal): ', response['outputs']['Scenario']['Site']['Generator']["fuel_used_gal"])
            print('Generator fuel use BAU (gal): ', response['outputs']['Scenario']['Site']['Generator']["fuel_used_gal_bau"])

            # print('NOx cost Grid: ', response['inputs']['Scenario']['Site']['Financial']["nox_cost_us_dollars_per_tonne_grid"])
            # print('SO2 cost Grid: ', response['inputs']['Scenario']['Site']['Financial']["so2_cost_us_dollars_per_tonne_grid"])
            # print('PM25 cost Fuelburn: ', response['inputs']['Scenario']['Site']['Financial']["pm25_cost_us_dollars_per_tonne_onsite_fuelburn"])
            
            # Values specific to Austin, TX (30.2672, -97.7431)
            self.assertEqual(round(inputs["Financial"]["nox_cost_us_dollars_per_tonne_grid"],3), round(4534.03247048984,3),
                             "Unexpected nox_cost_us_dollars_per_tonne_grid output from EASIUR ")
            self.assertEqual(inputs["Financial"]["pm25_cost_us_dollars_per_tonne_grid"], 126293.11077362332,
                             "Unexpected pm25_cost_us_dollars_per_tonne_grid output from EASIUR ")
            self.assertEqual(inputs["Financial"]["nox_cost_us_dollars_per_tonne_onsite_fuelburn"], 5965.834705734121,
                             "Unexpected nox_cost_us_dollars_per_tonne_onsite_fuelburn output from EASIUR ")
            self.assertEqual(inputs["Financial"]["pm25_cost_us_dollars_per_tonne_onsite_fuelburn"], 240382.50164494125,
                             "Unexpected pm25_cost_us_dollars_per_tonne_onsite_fuelburn output from EASIUR ")                

            for item in ['CO2', 'NOx', 'SO2', 'PM25']:
              print('Year 1 {} t: '.format(item), response['outputs']['Scenario']['Site']['year_one_emissions_t{}'.format(item)])
              print('Year 1 {} t BAU: '.format(item), response['outputs']['Scenario']['Site']['year_one_emissions_t{}_bau'.format(item)])
              
              print('Generator Year 1 {} t: '.format(item), response['outputs']['Scenario']['Site']['Generator']['year_one_emissions_t{}'.format(item)])
              print('Generator Year 1 {} t BAU: '.format(item), response['outputs']['Scenario']['Site']['Generator']['year_one_emissions_t{}_bau'.format(item)])

            #print('year_one_CO2_emissions_from_fuelburn: ', response['outputs']['Scenario']['Site']['year_one_CO2_emissions_from_fuelburn'])

            #print('year_one_CO2_emissions_from_elec_grid_purchase: ', response['outputs']["Scenario"]["Site"]["year_one_CO2_emissions_from_elec_grid_purchase"] )
            #print('year_one_CO2_emissions_from_elec_grid_purchase_bau: ', response['outputs']["Scenario"]["Site"]["year_one_CO2_emissions_from_elec_grid_purchase_bau"] )
            
            print('Lifecycle tonne CO2: ', response['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2'])
            print('Lifecycle tonne CO2 BAU: ', response['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2_bau'])
            print('Lifecycle cost CO2: ', response['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2'])
            print('Lifecycle cost CO2 BAU: ', response['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2_bau'])

            print('Lifecycle cost Health: ', response['outputs']['Scenario']['Site']['lifecycle_emissions_cost_Health'])
            print('Lifecycle cost Health BAU: ', response['outputs']['Scenario']['Site']['lifecycle_emissions_cost_Health_bau'])

            ## TODO: add these results 
            # self.nested_outputs["Scenario"]["Site"]["lifecycle_emissions_tNOx"] = self.results_dict.get("lifecycle_emissions_tNOx")
            # self.nested_outputs["Scenario"]["Site"]["lifecycle_emissions_tNOx_bau"] = self.results_dict.get("lifecycle_emissions_tNOx_bau")
            # self.nested_outputs["Scenario"]["Site"]["lifecycle_emissions_tSO2"] = self.results_dict.get("lifecycle_emissions_tSO2")
            # self.nested_outputs["Scenario"]["Site"]["lifecycle_emissions_tSO2_bau"] = self.results_dict.get("lifecycle_emissions_tSO2_bau")
            # self.nested_outputs["Scenario"]["Site"]["lifecycle_emissions_tPM25"] = self.results_dict.get("lifecycle_emissions_tPM25")
            # self.nested_outputs["Scenario"]["Site"]["lifecycle_emissions_tPM25_bau"] = self.results_dict.get("lifecycle_emissions_tPM25_bau")
            # "lifecycle_emissions_cost_Health_bau" 
            # "lifecycle_emissions_cost_Health" 
            
            ## path = 'reo/tests/outputs/'
            ## json.dump(response, open(path+'/'+"lifecycle_emissions_results.json", "w"))

            # output_df = pd.DataFrame()
            # output_df['load'] = response['outputs']['Scenario']['Site']['LoadProfile']['year_one_electric_load_series_kw']
            # output_df['load_met'] = response['outputs']['Scenario']['Site']['LoadProfile']['load_met_series_kw']

            #output_df.to_csv('reo/tests/outputs/test_load_constraints.csv')

            # self.assertEqual(pv_out['size_kw'], expected_pv_size,
            #                  "AC size ({}) does not equal expected AC size ({})."
            #                  .format(pv_out['size_kw'], expected_pv_size))

            
        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e

    # def test_no_techs(self):

    #     response = self.get_response(self.post_no_techs)
        
    #     region_expected = 'Upper Midwest' # lat long is Minneapolis
    #     CO2_t_yr1_expected = 16962.85 / 2204.62 
    #     NOx_t_yr1_expected = 11.66 / 2204.62

    #     region_out = response['outputs']['Scenario']['Site']['ElectricTariff']['emissions_region']
    #     CO2_t_yr1_out = response['outputs']['Scenario']['Site']['year_one_emissions_tCO2']
    #     NOx_t_yr1_out = response['outputs']['Scenario']['Site']['year_one_emissions_tNOx']
        
    #     messages = response['messages']

    #     try:
    #         self.assertEqual(region_out, region_expected,
    #                          "Region ({}) does not equal expected Region ({})."
    #                          .format(region_out, region_expected))
            
    #         self.assertEqual(CO2_t_yr1_out, CO2_t_yr1_expected,
    #                          "tonne CO2 in yr 1 ({}) expected tonne CO2 in yr 1 ({})."
    #                          .format(CO2_t_yr1_out, CO2_t_yr1_expected))
            
    #         self.assertEqual(NOx_t_yr1_out, NOx_t_yr1_expected,
    #                          "tonne NOx in yr 1 ({}) expected tonne NOx in yr 1 ({})."
    #                          .format(NOx_t_yr1_out, NOx_t_yr1_expected))

    #         print('Emissions Region: ', response['outputs']['Scenario']['Site']['ElectricTariff']['emissions_region'])
    #         print('PV size: ', response['outputs']['Scenario']['Site']['PV']['size_kw'])
    #         print('Batt kWh: ', response['outputs']['Scenario']['Site']['Storage']['size_kwh'])
    #         print('Batt kW: ', response['outputs']['Scenario']['Site']['Storage']['size_kw'])
    #         print('Generator kW: ', response['outputs']['Scenario']['Site']['Generator']['size_kw'])
    #         print('Annual Load kWh: ', response['outputs']['Scenario']['Site']["LoadProfile"]["annual_calculated_kwh"])
    #         print('Year 1 kWh from grid: ', response['outputs']['Scenario']['Site']["ElectricTariff"]["year_one_energy_supplied_kwh"])
    #         print('Year 1 kWh from grid BAU: ', response['outputs']['Scenario']['Site']["ElectricTariff"]["year_one_energy_supplied_kwh_bau"])
            

    #         for item in ['CO2', 'NOx', 'SO2', 'PM25']:
    #           print('Year 1 {}: '.format(item), response['outputs']['Scenario']['Site']['year_one_emissions_t{}'.format(item)])
    #           # print('Year 1 {} BAU: '.format(item), response['outputs']['Scenario']['Site']['year_one_emissions_bau_t{}'.format(item)])
              
    #         print('fuel_used_gal: ', response['outputs']['Scenario']['Site']['Generator']['fuel_used_gal'])
    #         print('year_one_CO2_emissions_from_fuelburn: ', response['outputs']['Scenario']['Site']['year_one_CO2_emissions_from_fuelburn'])
    #         print('Lifecycle tonne CO2: ', response['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2'])
    #         # print('Lifecycle tonne CO2 BAU: ', response['outputs']['Scenario']['Site']['lifecycle_emissions_tCO2_bau'])
    #         print('Lifecycle cost CO2: ', response['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2'])
    #         # print('Lifecycle cost CO2 BAU: ', response['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2_bau'])

    #         print('Lifecycle cost Health: ', response['outputs']['Scenario']['Site']['lifecycle_emissions_cost_Health'])
    #         # print('Lifecycle cost Health BAU: ', response['outputs']['Scenario']['Site']['lifecycle_emissions_cost_Health_bau'])
            
    #         ## path = 'reo/tests/outputs/'
    #         ## json.dump(response, open(path+'/'+"lifecycle_emissions_results.json", "w"))

    #         # output_df = pd.DataFrame()
    #         # output_df['load'] = response['outputs']['Scenario']['Site']['LoadProfile']['year_one_electric_load_series_kw']
    #         # output_df['load_met'] = response['outputs']['Scenario']['Site']['LoadProfile']['load_met_series_kw']

    #         #output_df.to_csv('reo/tests/outputs/test_load_constraints.csv')

            
    #     except Exception as e:
    #         error_msg = None
    #         if hasattr(messages, "error"):
    #             error_msg = messages.error
    #         print("test_flex_tech API error message: {}".format(error_msg))
    #         print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
    #         raise e

