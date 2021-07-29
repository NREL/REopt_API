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


class TestNOx(ResourceTestCaseMixin, TestCase):
    """
    Test lifetime climate and health emissions calculations
    """

    def setUp(self):
        super(TestNOx, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'

        self.post = {
          "Scenario": {
            "time_steps_per_hour": 1,
            "include_climate_in_objective": True,
            "include_health_in_objective": True,
            "Site": {
              "longitude": -91.7337,
              "latitude": 35.2468,
              "roof_squarefeet": None,
              "land_acres": None,
              "PV": {
                "pbi_years": 1.0,
                "macrs_bonus_pct": 0.0,
                "max_kw": 200.0,
                "pbi_max_us_dollars": 1000000000.0,
                "radius": 0.0,
                "state_ibi_pct": 0.0,
                "state_rebate_us_dollars_per_kw": 0.0,
                "installed_cost_us_dollars_per_kw": 2000.0,
                "utility_ibi_max_us_dollars": 10000000000.0,
                "tilt": 10.0,
                "degradation_pct": 0.005,
                "gcr": 0.4,
                "pbi_system_max_kw": 1000000000.0,
                "utility_ibi_pct": 0.0,
                "state_ibi_max_us_dollars": 10000000000.0,
                "utility_rebate_max_us_dollars": 10000000000.0,
                "macrs_option_years": 5,
                "state_rebate_max_us_dollars": 10000000000.0,
                "dc_ac_ratio": 1.1,
                "federal_itc_pct": 0.3,
                "existing_kw": 0.0,
                "module_type": 0,
                "array_type": 1,
                "pbi_us_dollars_per_kwh": 0.0,
                "om_cost_us_dollars_per_kw": 16.0,
                "utility_rebate_us_dollars_per_kw": 0.0,
                "min_kw": 0.0,
                "losses": 0.14,
                "macrs_itc_reduction": 0.5,
                "federal_rebate_us_dollars_per_kw": 0.0,
                "inv_eff": 0.96,
                "azimuth": 180.0
              },
              "Generator": {
                "om_cost_us_dollars_per_kwh": 0.01,
                "max_kw": 0.0,
                "min_kw": 0.0,
                "existing_kw": 0.0,
                "pbi_max_us_dollars": 0.0,
                "state_ibi_pct": 0.0,
                "generator_only_runs_during_grid_outage": False,
                "utility_rebate_max_us_dollars": 0.0,
                "installed_cost_us_dollars_per_kw": 600.0,
                "utility_ibi_max_us_dollars": 0.0,
                "fuel_avail_gal": 1000000000.0,
                "diesel_fuel_cost_us_dollars_per_gallon": 3.0,
                "fuel_slope_gal_per_kwh": 0.0,
                "state_rebate_us_dollars_per_kw": 0.0,
                "macrs_option_years": 0,
                "state_rebate_max_us_dollars": 0.0,
                "federal_itc_pct": 0.0,
                "pbi_us_dollars_per_kwh": 0.0,
                "om_cost_us_dollars_per_kw": 10.0,
                "utility_rebate_us_dollars_per_kw": 0.0,
                "macrs_itc_reduction": 0.0,
                "federal_rebate_us_dollars_per_kw": 0.0,
                "generator_sells_energy_back_to_grid": False
              },
              "LoadProfile": {
                "critical_loads_kw_is_net": False,
                "year": 2017,
                "loads_kw_is_net": True,
                "outage_start_time_step": None,
                "outage_end_time_step": None,
                "monthly_totals_kwh": [],
                "critical_load_pct": 0.5,
                "loads_kw": [],
                "outage_is_major_event": True,
                "critical_loads_kw": [],
                "doe_reference_name": "MidriseApartment",
                "annual_kwh": 259525.0
              },
              "Storage": {
                "max_kwh": 0.0,
                "rectifier_efficiency_pct": 0.96,
                "total_itc_pct": 0.0,
                "min_kw": 0.0,
                "max_kw": 0.0,
                "min_kwh": 0.0,
                "replace_cost_us_dollars_per_kw": 460.0,
                "replace_cost_us_dollars_per_kwh": 230.0,
                "installed_cost_us_dollars_per_kw": 1000.0,
                "total_rebate_us_dollars_per_kw": 0,
                "installed_cost_us_dollars_per_kwh": 500.0,
                "inverter_efficiency_pct": 0.96,
                "battery_replacement_year": 10,
                "canGridCharge": True,
                "macrs_bonus_pct": 0.0,
                "macrs_itc_reduction": 0.5,
                "macrs_option_years": 7,
                "internal_efficiency_pct": 0.975,
                "soc_min_pct": 0.2,
                "soc_init_pct": 0.5,
                "inverter_replacement_year": 10
              },
              "ElectricTariff": {
                "emissions_factor_series_lb_CO2_per_kwh": [1.0],
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
                "value_of_lost_load_us_dollars_per_kwh": 100.0,
                "analysis_years": 25,
                "microgrid_upgrade_cost_pct": 0.3,
                "offtaker_tax_pct": 0.26,
                "om_cost_escalation_pct": 0.025,
                "co2_cost_us_dollars_per_tonne": 51.0,
                "nox_cost_us_dollars_per_tonne": 51.0, # TODO: change to values from EASIUR! (and also make seasonal?)
                "so2_cost_us_dollars_per_tonne": 51.0, # TODO: change to values from EASIUR! 
                "pm_cost_us_dollars_per_tonne": 51.0 # TODO: change to values from EASIUR! 
              },
              "Wind": {
                "pbi_years": 1.0,
                "macrs_bonus_pct": 0.0,
                "max_kw": 0.0,
                "min_kw": 0.0,
                "pbi_max_us_dollars": 1000000000.0,
                "wind_meters_per_sec": None,
                "state_ibi_pct": 0.0,
                "utility_rebate_max_us_dollars": 10000000000.0,
                "installed_cost_us_dollars_per_kw": 3013.0,
                "utility_ibi_max_us_dollars": 10000000000.0,
                "pressure_atmospheres": None,
                "pbi_system_max_kw": 1000000000.0,
                "utility_ibi_pct": 0.0,
                "state_ibi_max_us_dollars": 10000000000.0,
                "wind_direction_degrees": None,
                "state_rebate_us_dollars_per_kw": 0.0,
                "macrs_option_years": 5,
                "state_rebate_max_us_dollars": 10000000000.0,
                "federal_itc_pct": 0.3,
                "temperature_celsius": None,
                "pbi_us_dollars_per_kwh": 0.0,
                "om_cost_us_dollars_per_kw": 35.0,
                "utility_rebate_us_dollars_per_kw": 0.0,
                "macrs_itc_reduction": 0.5,
                "federal_rebate_us_dollars_per_kw": 0.0
              }
            }
          }
        }

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
                "nox_cost_us_dollars_per_tonne": 51.0, # TODO: change to values from EASIUR! (and also make seasonal?)
                "so2_cost_us_dollars_per_tonne": 51.0, # TODO: change to values from EASIUR! 
                "pm_cost_us_dollars_per_tonne": 51.0 # TODO: change to values from EASIUR! 
              },
              "Wind": {
                "max_kw": 0.0,
                "min_kw": 0.0
              }
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

        response = self.get_response(self.post)
        
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
            

            for item in ['CO2', 'NOx', 'SO2', 'PM']:
              print('Year 1 {}: '.format(item), response['outputs']['Scenario']['Site']['year_one_emissions_lb_{}'.format(item)])
              print('Year 1 {} BAU: '.format(item), response['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_{}'.format(item)])
              
              print('Generator Year 1 {}: '.format(item), response['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_{}'.format(item)])
              print('Generator Year 1 {} BAU: '.format(item), response['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_{}'.format(item)])

            print('fuel_used_gal: ', response['outputs']['Scenario']['Site']['Generator']['fuel_used_gal'])
            print('year_one_CO2_emissions_from_fuelburn: ', response['outputs']['Scenario']['Site']['year_one_CO2_emissions_from_fuelburn'])
            print('Lifetime lbs CO2: ', response['outputs']['Scenario']['Site']['lifetime_emissions_lb_CO2'])
            print('Lifetime lbs CO2 BAU: ', response['outputs']['Scenario']['Site']['lifetime_emissions_lb_CO2_bau'])
            print('Lifetime cost CO2: ', response['outputs']['Scenario']['Site']['lifetime_emissions_cost_CO2'])
            print('Lifetime cost CO2 BAU: ', response['outputs']['Scenario']['Site']['lifetime_emissions_cost_CO2_bau'])

            print('Lifetime cost Health: ', response['outputs']['Scenario']['Site']['lifetime_emissions_cost_Health'])
            print('Lifetime cost Health BAU: ', response['outputs']['Scenario']['Site']['lifetime_emissions_cost_Health_bau'])

            ## TODO: add these results 
            # self.nested_outputs["Scenario"]["Site"]["lifetime_emissions_lb_NOx"] = self.results_dict.get("lifetime_emissions_lb_NOx")
            # self.nested_outputs["Scenario"]["Site"]["lifetime_emissions_lb_NOx_bau"] = self.results_dict.get("lifetime_emissions_lb_NOx_bau")
            # self.nested_outputs["Scenario"]["Site"]["lifetime_emissions_lb_SO2"] = self.results_dict.get("lifetime_emissions_lb_SO2")
            # self.nested_outputs["Scenario"]["Site"]["lifetime_emissions_lb_SO2_bau"] = self.results_dict.get("lifetime_emissions_lb_SO2_bau")
            # self.nested_outputs["Scenario"]["Site"]["lifetime_emissions_lb_PM"] = self.results_dict.get("lifetime_emissions_lb_PM")
            # self.nested_outputs["Scenario"]["Site"]["lifetime_emissions_lb_PM_bau"] = self.results_dict.get("lifetime_emissions_lb_PM_bau")
            # "lifetime_emissions_cost_Health_bau" 
            # "lifetime_emissions_cost_Health" 
            
            ## path = 'reo/tests/outputs/'
            ## json.dump(response, open(path+'/'+"lifetime_emissions_results.json", "w"))

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
            print("test_flex_tech API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e

    def test_no_techs(self):

        response = self.get_response(self.post_no_techs)
        
        region_expected = 'Upper Midwest' # lat long is Minneapolis
        CO2_lb_yr1_expected = 16962.85 
        NOx_lb_yr1_expected = 11.66

        region_out = response['outputs']['Scenario']['Site']['ElectricTariff']['emissions_region']
        CO2_lb_yr1_out = response['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2']
        NOx_lb_yr1_out = response['outputs']['Scenario']['Site']['year_one_emissions_lb_NOx']
        
        messages = response['messages']

        try:
            self.assertEqual(region_out, region_expected,
                             "Region ({}) does not equal expected Region ({})."
                             .format(region_out, region_expected))
            
            self.assertEqual(CO2_lb_yr1_out, CO2_lb_yr1_expected,
                             "lb CO2 in yr 1 ({}) expected lb CO2 in yr 1 ({})."
                             .format(CO2_lb_yr1_out, CO2_lb_yr1_expected))
            
            self.assertEqual(NOx_lb_yr1_out, NOx_lb_yr1_expected,
                             "lb NOx in yr 1 ({}) expected lb NOx in yr 1 ({})."
                             .format(NOx_lb_yr1_out, NOx_lb_yr1_expected))

            print('Emissions Region: ', response['outputs']['Scenario']['Site']['ElectricTariff']['emissions_region'])
            print('PV size: ', response['outputs']['Scenario']['Site']['PV']['size_kw'])
            print('Batt kWh: ', response['outputs']['Scenario']['Site']['Storage']['size_kwh'])
            print('Batt kW: ', response['outputs']['Scenario']['Site']['Storage']['size_kw'])
            print('Generator kW: ', response['outputs']['Scenario']['Site']['Generator']['size_kw'])
            print('Annual Load kWh: ', response['outputs']['Scenario']['Site']["LoadProfile"]["annual_calculated_kwh"])
            print('Year 1 kWh from grid: ', response['outputs']['Scenario']['Site']["ElectricTariff"]["year_one_energy_supplied_kwh"])
            print('Year 1 kWh from grid BAU: ', response['outputs']['Scenario']['Site']["ElectricTariff"]["year_one_energy_supplied_kwh_bau"])
            

            for item in ['CO2', 'NOx', 'SO2', 'PM']:
              print('Year 1 {}: '.format(item), response['outputs']['Scenario']['Site']['year_one_emissions_lb_{}'.format(item)])
              # print('Year 1 {} BAU: '.format(item), response['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_{}'.format(item)])
              
            print('fuel_used_gal: ', response['outputs']['Scenario']['Site']['Generator']['fuel_used_gal'])
            print('year_one_CO2_emissions_from_fuelburn: ', response['outputs']['Scenario']['Site']['year_one_CO2_emissions_from_fuelburn'])
            print('Lifetime lbs CO2: ', response['outputs']['Scenario']['Site']['lifetime_emissions_lb_CO2'])
            # print('Lifetime lbs CO2 BAU: ', response['outputs']['Scenario']['Site']['lifetime_emissions_lb_CO2_bau'])
            print('Lifetime cost CO2: ', response['outputs']['Scenario']['Site']['lifetime_emissions_cost_CO2'])
            # print('Lifetime cost CO2 BAU: ', response['outputs']['Scenario']['Site']['lifetime_emissions_cost_CO2_bau'])

            print('Lifetime cost Health: ', response['outputs']['Scenario']['Site']['lifetime_emissions_cost_Health'])
            # print('Lifetime cost Health BAU: ', response['outputs']['Scenario']['Site']['lifetime_emissions_cost_Health_bau'])
            
            ## path = 'reo/tests/outputs/'
            ## json.dump(response, open(path+'/'+"lifetime_emissions_results.json", "w"))

            # output_df = pd.DataFrame()
            # output_df['load'] = response['outputs']['Scenario']['Site']['LoadProfile']['year_one_electric_load_series_kw']
            # output_df['load_met'] = response['outputs']['Scenario']['Site']['LoadProfile']['load_met_series_kw']

            #output_df.to_csv('reo/tests/outputs/test_load_constraints.csv')

            
        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("test_flex_tech API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e

