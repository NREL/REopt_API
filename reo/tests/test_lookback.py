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
from reo.models import ModelManager
import os


class TestLookback(ResourceTestCaseMixin, TestCase):
    """
    Documentation
    """

    def setUp(self):
        super(TestLookback, self).setUp()

        self.reopt_base = '/v1/job/'
        self.post = {
            "Scenario": {
              "timeout_seconds": 400,
              "optimality_tolerance_techs": 0.01,
              "Site": {
                "latitude": 35.31,
                "longitude": 138.87,
                "Financial": {
                  "om_cost_escalation_pct": 0.0,
                  "escalation_pct": 0.0,
                  "offtaker_tax_pct": 0.0,
                  "offtaker_discount_pct": 0.0,
                  "third_party_ownership": False,
                  "owner_tax_pct": 0.0,
                  "owner_discount_pct": 0.0,
                  "analysis_years": 1,
                  "value_of_lost_load_us_dollars_per_kwh": 0,
                  "microgrid_upgrade_cost_pct": 0.0
                },
                "LoadProfile": {
                  "doe_reference_name": "Hospital",
                  "percent_share": [100.0],
                  "loads_kw": [1.0]*8760,
                  "year": 2020,
                  "loads_kw_is_net": True,
                  "critical_load_pct": 0.5,
                  "outage_is_major_event": True
                },
                "ElectricTariff": {
                  "urdb_response": {},
                  "net_metering_limit_kw": 0.0,
                  "interconnection_limit_kw": 100000000.0,
                  "add_tou_energy_rates_to_urdb_rate": True,
                  "tou_energy_rates_us_dollars_per_kwh": [0.01]*8760 
                },
                "PV": {
                  "min_kw": 0.0,
                  "max_kw": 0.0
                },
                "Storage": {
                  "min_kw": 0.0,
                  "max_kw": 0,
                  "min_kwh": 0.0,
                  "max_kwh": 0,
                }
              }
            }
          } 
        urdb_base_path = os.path.join('reo', 'tests', 'posts', 'lookback_urdb_base.json')
        with open(urdb_base_path, 'r') as fp:
          URDB1 = json.load(fp)
        self.post["Scenario"]["Site"]["ElectricTariff"]["urdb_response"] = URDB1
        urdb_add = {"lookbackMonths": [1]*12,
                    "lookbackPercent": 1.0,
                    "lookbackRange": 0,
                    "flatdemandstructure": [[{"rate": 15.97}]],
                    "flatdemandmonths": [0]*12
                    }
        self.post["Scenario"]["Site"]["ElectricTariff"]["urdb_response"].update(urdb_add)

        # Toggle double the demand based on single hour increase (12 month lookback)
        self.post["Scenario"]["Site"]["LoadProfile"]["loads_kw"][3] = 2.0

    def get_response(self, data):

        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_lookback(self):
        
        resp = self.get_response(data=self.post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        dummy = 3