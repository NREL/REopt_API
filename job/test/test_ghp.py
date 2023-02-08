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
from cProfile import run
import json
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
import os
import logging
import requests
logging.disable(logging.CRITICAL)
import os
import json
from job.models import APIMeta, GHPOutputs

class TestGHP(ResourceTestCaseMixin, TestCase):    
    
    def setUp(self):
        super(TestGHP, self).setUp()
        self.test_ghpghx_post = os.path.join('ghpghx', 'tests', 'posts', 'test_ghpghx_POST.json')
        self.ghpghx_response = os.path.join('job', 'test', 'posts', 'ghpghx_response.json')
        self.ghp_results = os.path.join('julia_src', 'ghp_results.json')

    def test_ghp(self):
        """
        Minimal test case for adding GHP to job app
        """
        scenario = {
            "Settings": {"run_bau": False},
            "Site": {"longitude": -118.1164613, "latitude": 34.5794343},
            "ElectricTariff": {"blended_annual_energy_rate": 0.1, "blended_annual_demand_rate": 10.0},
            "ExistingBoiler": {
                "fuel_cost_per_mmbtu": 10
            },            
            "GHP": {
                "building_sqft": 50000.0,
                "require_ghp_purchase": True,
                "space_heating_efficiency_thermal_factor": 0.85,
                "cooling_efficiency_thermal_factor": 0.6
            },
            "ElectricLoad": {
                "doe_reference_name": "Hospital"
            },
            "CoolingLoad": {
                "doe_reference_name": "Hospital"
            },
            "SpaceHeatingLoad": {
                "doe_reference_name": "Hospital"
            },
            "DomesticHotWaterLoad": {
                "doe_reference_name": "Hospital"
            },            
            "PV": {"max_kw": 0.0},
            "ElectricStorage":{"max_kw": 0.0, "max_kwh": 0.0}            
        }

        ghpghx_post = json.load(open(self.test_ghpghx_post, 'rb'))
        ghpghx_response = json.load(open(self.ghpghx_response, 'rb'))

        scenario["GHP"]["ghpghx_inputs"] = [ghpghx_post]
        scenario["GHP"]["ghpghx_inputs"][0]["max_sizing_iterations"] = 1
        scenario["GHP"]["ghpghx_responses"] = [ghpghx_response]
        # json.dump(scenario, open("scenario.json", "w"))

        # ghp_results = json.load(open(self.ghp_results, 'rb'))
        # ghp_outputs = ghp_results["GHP"]

        # resp = self.api_client.post('/dev/job/', format='json', data=scenario)
        # self.assertHttpCreated(resp)
        # r = json.loads(resp.content)
        # run_uuid = r.get('run_uuid')

        # meta = APIMeta.objects.get(run_uuid=run_uuid)
        # meta.status = results.get("status")
        # meta.save(update_fields=["status"])

        # GHPOutputs.create(meta=meta, **ghp_outputs).save()
        # GHPOutputs.create(**ghp_outputs).save()

        resp = self.api_client.post('/dev/job/', format='json', data=scenario)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        
        resp = self.api_client.get(f'/dev/job/{run_uuid}/results')
        r = json.loads(resp.content)
        inputs = r["inputs"]
        results = r["outputs"]

        self.assertIn("CoolingLoad", list(results.keys()))
        self.assertIn("HeatingLoad", list(results.keys()))
        self.assertIn("GHP", list(inputs.keys()))       
        self.assertIn("GHP", list(results.keys()))
        self.assertIn("ExistingChiller",list(results.keys()))
        self.assertIn("ExistingBoiler", list(results.keys()))

        # json.dump(r, open("ghp_response.json", "w"))