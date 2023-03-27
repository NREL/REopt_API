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
import pandas as pd
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
from reo.models import ModelManager

class GHPTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(GHPTest, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_reopt_post = os.path.join('reo', 'tests', 'posts', 'test_ghp_hybrid_POST.json')
        self.test_ghpghx_post = os.path.join('ghpghx', 'tests', 'posts', 'test_hybrid_ghpghx_POST.json')

    def get_ghpghx_response(self, data):
        return self.api_client.post(self.ghpghx_base, format='json', data=data)

    def get_reopt_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_ghp(self):
        """

        This tests the automatic sizing functionality of hybrid GHP

        """
        nested_data = json.load(open(self.test_reopt_post, 'rb'))
        ghpghx_post = json.load(open(self.test_ghpghx_post, 'rb'))

        nested_data["Scenario"]["Site"]["GHP"]["ghpghx_inputs"] = [ghpghx_post]
        
        # Call REopt
        resp = self.get_reopt_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        ghp_uuid = d["outputs"]["Scenario"]["Site"]["GHP"]["ghp_chosen_uuid"]
        print("GHP uuid chosen = ", ghp_uuid)

        # Output number of boreholes and heatpump sizing 
        n_boreholes = d["outputs"]["Scenario"]["Site"]["GHP"]["ghpghx_chosen_outputs"]["number_of_boreholes"]
        heatpump_tons = d["outputs"]["Scenario"]["Site"]["GHP"]["ghpghx_chosen_outputs"]["peak_combined_heatpump_thermal_ton"]
        # Comparison to TESS exe range
        self.assertAlmostEqual(n_boreholes, 45)
        self.assertAlmostEqual(heatpump_tons, 824.927)
