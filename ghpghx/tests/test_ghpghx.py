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
import os
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
import pandas as pd
from ghpghx.models import ModelManager

class TestGHPGHX(ResourceTestCaseMixin, TestCase): 
    """
    Test GHPGHX model
    """
   
    def setUp(self):
        # setUp() is a standard method which is run for every test (in addition to __init__())
        super(TestGHPGHX, self).setUp()
        self.ghpghx_base = '/v1/ghpghx/'
        self.test_post_base = os.path.join('ghpghx', 'tests', 'posts', 'test_ghp_POST.json')

    def get_response(self, data):
        #response = self.api_client.get(self.views_endpoint_base, data=params_dict)
        response = self.api_client.post(self.ghpghx_base, format='json', data=data)
        return response

    def test_ghpghx(self):
        # test_params_dict = {"year": 2017,
        #                     "chp_prime_mover": "recip_engine"}
        
        # Base post for GHPGHX which includes scalar values, mostly parameters
        self.post = json.load(open(self.test_post_base, 'rb'))

        # Ambient temperature profile, and heating and cooling load profiles from .dat file
        # Not sure how python appends the two header lines; Julia uses "_" to separate header text
        temps_loads_file = os.path.join('ghpghx', 'tests', 'posts', 'BuildingLoads.dat')
        temps_loads_df = pd.read_csv(temps_loads_file, sep='\s+', header=0, skiprows=[1])
        #self.post["ambient_temperature_f"] = list(temps_loads_df["Temp"].values)
        self.post["heating_thermal_load_mmbtu_per_hr"] = list(temps_loads_df["Heating"].values / 1.0E6)
        self.post["cooling_thermal_load_ton"] = list(temps_loads_df["Cooling"].values / 12000.0)

        # Heat pump performance maps
        hp_cop_filepath = os.path.join('ghpghx', 'tests', 'posts', "heatpump_cop_map.csv" )
        heatpump_copmap_df = pd.read_csv(hp_cop_filepath)
        heatpump_copmap_list_of_dict = heatpump_copmap_df.to_dict('records')
        self.post["cop_map_eft_heating_cooling"] = heatpump_copmap_list_of_dict

        resp = self.get_response(data=self.post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)

        # Now we should have ghp_uuid from the POST response, and we now need to simulate the /results endpoint to get the data
        # We could instead GET the /results endpoint response using this ghp_uuid, but we have make_response internally
        ghp_uuid = r.get('ghp_uuid')
        results_url = "/v1/ghpghx/"+ghp_uuid+"/results/"
        resp = self.api_client.get(results_url)
        r = json.loads(resp.content)
        
        #d = ModelManager.make_response(ghp_uuid=ghp_uuid)
        #json.dump(d["inputs"], open("ghpghx_post.json", "w"))
        dummy = 3