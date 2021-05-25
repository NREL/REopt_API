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
import copy
import time
import numpy as np
import pandas as pd
from tastypie.test import ResourceTestCaseMixin
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from reo.models import ModelManager
from ghpghx.models import ModelManager as gModelManager
from reo.utilities import MMBTU_TO_KWH, TONHOUR_TO_KWHT

class GHPTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(GHPTest, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_reopt_post = os.path.join('reo', 'tests', 'posts', 'test_ghp_POST.json')
        self.test_ghpghx_post = os.path.join('ghpghx', 'tests', 'posts', 'test_ghpghx_POST.json')

    def get_ghpghx_response(self, data):
        return self.api_client.post(self.ghpghx_base, format='json', data=data)

    def get_reopt_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_ghp(self):
        """
        GHP Testing
        """

        # Call to GHPGHX app to run GHPGHX model and return the "ghpghx_response" as input to REopt
        #   this mimicks the process the webtool (and API users) would call GHPGHX then REopt
        nested_data = json.load(open(self.test_reopt_post, 'rb'))
        ghpghx_post = json.load(open(self.test_ghpghx_post, 'rb'))

        # Heat pump performance maps
        hp_cop_filepath = os.path.join('ghpghx', 'tests', 'posts', "heatpump_cop_map.csv" )
        heatpump_copmap_df = pd.read_csv(hp_cop_filepath)
        heatpump_copmap_list_of_dict = heatpump_copmap_df.to_dict('records')
        ghpghx_post["cop_map_eft_heating_cooling"] = heatpump_copmap_list_of_dict

        nested_data["Scenario"]["Site"]["GHP"]["ghpghx_inputs"] = [ghpghx_post]

        # Call API, get results in "d" dictionary
        nested_data["Scenario"]["timeout_seconds"] = 420  # Overwriting
        nested_data["Scenario"]["optimality_tolerance_techs"] = 0.01  # Overwriting
        nested_data["Scenario"]["optimality_tolerance_bau"] = 0.001                                                                    
        
        # Call REopt
        resp = self.get_reopt_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        ghp_uuid = d["outputs"]["Scenario"]["Site"]["GHP"]["ghp_chosen_uuid"]
        print("GHP uuid chosen = ", ghp_uuid)

        #TODO index into the ghp_response with ghp_uuid to get GHP results
        # Could add actual index to outputs to index on list_of_dict instead, but that would be redundant
        # could instead get ghp_uuid after getting index of list_of_dict, but maybe we could instead do a 
        # ModelManager call in process_results to assign the chosen ghp_response
