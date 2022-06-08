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
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
from reo.models import ModelManager
import numpy as np


class InternationalPVTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(InternationalPVTest, self).setUp()
        self.reopt_base = '/v2/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_indonesia_pv(self):
        """
        Test PV output for international site (in Indonesia) that 
        falls within new bounds of NSRDB HIMIWARI data for SE Asia.
        :return:
        """

        nested_data = {"Scenario": {
                "Site": {
                    "longitude": 130.1452734,
                    "latitude": -3.2384616, 
                "PV": {
                    "min_kw": 1000,
                    "max_kw": 1000,
                    'array_type': 0,
                    'degradation_pct': 0.0
                },
                "LoadProfile": {
                    "doe_reference_name": "FlatLoad",
                    "annual_kwh": 10000000.0,
                    "city": "LosAngeles"
                },
                "ElectricTariff": {
                    "urdb_label": "5ed6c1a15457a3367add15ae"
                },
                "Financial": {
                    "escalation_pct": 0.026,
                    "analysis_years": 25
                }
            }}}

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        messages = d['messages']

        a = d["outputs"]["Scenario"]["Site"]["PV"]
        pv_list = a['year_one_to_battery_series_kw'], a['year_one_to_load_series_kw'], a['year_one_to_grid_series_kw'], a['year_one_curtailed_production_series_kw']
        tot_pv = np.sum(pv_list, axis=0)
        total_pv = sum(tot_pv)
        print(total_pv)

        try:
            self.assertAlmostEqual(total_pv, 1246915, delta=0.5) # checked against PVWatts online calculator

        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("NegativeLatitudeTest API error message: {}".format(error_msg))
            print("Run uuid: {}".format(d['outputs']['Scenario']['run_uuid']))
            raise e

