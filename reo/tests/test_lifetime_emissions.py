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
            # Expected results 
            self.assertEqual(response['outputs']['Scenario']['Site']['PV']['size_kw'], 4.0064,
                             "Unexpected PV Size")
            self.assertEqual(response['outputs']['Scenario']['Site']['lifecycle_emissions_cost_CO2'], 1245.53,
                             "Unexpected ['Site']['lifecycle_emissions_cost_CO2']")

            # Values specific to Austin, TX (30.2672, -97.7431)
            self.assertEqual(response['outputs']['Scenario']['Site']['ElectricTariff']['emissions_region'], 'Texas',
                             "Unexpected AVERT emissions_region.")
            self.assertEqual(round(inputs["Financial"]["nox_cost_us_dollars_per_tonne_grid"],3), round(4534.03247048984,3),
                             "Unexpected nox_cost_us_dollars_per_tonne_grid output from EASIUR ")
            self.assertEqual(inputs["Financial"]["pm25_cost_us_dollars_per_tonne_grid"], 126293.11077362332,
                             "Unexpected pm25_cost_us_dollars_per_tonne_grid output from EASIUR ")
            self.assertEqual(inputs["Financial"]["nox_cost_us_dollars_per_tonne_onsite_fuelburn"], 5965.834705734121,
                             "Unexpected nox_cost_us_dollars_per_tonne_onsite_fuelburn output from EASIUR ")
            self.assertEqual(inputs["Financial"]["pm25_cost_us_dollars_per_tonne_onsite_fuelburn"], 240382.50164494125,
                             "Unexpected pm25_cost_us_dollars_per_tonne_onsite_fuelburn output from EASIUR ")                

            
        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e