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


class TestBreakevenCost(ResourceTestCaseMixin, TestCase):
    """
    Test breakeven cost of CO2: "breakeven_cost_of_emissions_reduction_us_dollars_per_tCO2"
    """

    def setUp(self):
        super(TestBreakevenCost, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'

        self.post = {
          "Scenario": {
            "time_steps_per_hour": 1,
            "include_climate_in_objective": False,
            "include_health_in_objective": False,
            "add_soc_incentive": True,
            "off_grid_flag": False, 
            "Site": {
              "longitude": -75.51491279999999, # Phoenixville, PA
              "latitude": 40.1303822,
              "PV": {
                "min_kw": 0.0,
                "max_kw": 1000000,
                "can_curtail": True, # False,
              },
              "Generator": {
                "existing_kw": 0.0,
                "min_kw": 0.0,
                "max_kw": 0.0,
              },
              "Storage": {
                "min_kw": 0.0,
                "max_kw": 0,
                "min_kwh": 0.0,
                "max_kwh": 0.0,  
              },
              "LoadProfile": {
                "year": 2020,
                "doe_reference_name": "Supermarket",
                "annual_kwh": 2018760
              },
              "ElectricTariff": {
                "net_metering_limit_kw": 0.0,
                "interconnection_limit_kw": 100000000.0,
                "urdb_label": "5a8330175457a3ef3c914215", # https://openei.org/apps/IURDB/rate/view/5a8330175457a3ef3c914215#2__Demand 
              },
              "Financial": {
                #"co2_cost_us_dollars_per_tonne": 51.0,
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
    

    def test_breakeven_cost(self):
        """
        Should be true: 
        For a PV-only analysis, the user sets an emissions constraint of 25% reduction in total (lifetime) 
        emissions, which results in a negative NPV. They see a $/t output of $X/t CO2 lifetime reduction 
        to “breakeven.” 
        They run another analysis with a 25% reduction and a $X/t CO2 input, fix the PV 
        to the previous sizing, and include CO2 costs in the objective function. The new NPV result is $0. 
        """

        self.post['Scenario']['Site']['co2_emissions_reduction_min_pct'] = 0.250
        self.post['Scenario']['Site']['co2_emissions_reduction_max_pct'] = 0.250

        response = self.get_response(self.post)
        inputs = response['inputs']['Scenario']['Site']
        outputs = response['outputs']['Scenario']['Site']
        messages = response['messages']

        try:
            
            pv_fixed_size = outputs['PV']["size_kw"]
            breakeven_cost = outputs["breakeven_cost_of_emissions_reduction_us_dollars_per_tCO2"]

            # Re-run with same % reduction, new co2 cost input, fix PV to previous sizing, include climate in obj
            self.post['Scenario']["include_climate_in_objective"] = True
            self.post['Scenario']['Site']['Financial']["co2_cost_us_dollars_per_tonne"] = breakeven_cost
            self.post['Scenario']['Site']['PV']["min_kw"] = pv_fixed_size
            self.post['Scenario']['Site']['PV']["max_kw"] = pv_fixed_size

            response = self.get_response(self.post)
            outputs = response['outputs']['Scenario']['Site']

            self.assertAlmostEqual(outputs['Financial']["npv_us_dollars"], 0.0, delta=5)
            
        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e