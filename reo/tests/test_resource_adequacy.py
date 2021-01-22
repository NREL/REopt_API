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
import copy
import os
import pandas as pd
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat
from django.test import TestCase  
from reo.models import ModelManager
from reo.utilities import check_common_outputs
from reo.validators import ValidateNestedInput
from reo.src.wind import WindSAMSDK, combine_wind_files
import logging
logging.disable(logging.CRITICAL)



event_day_flags = [0.0]*8760
event_day_flags[5000] = 1.0
event_day_flags[5050] = 1.0

ra_post = {"Scenario": {"Site": {
                "longitude": -105.2348,
                "latitude": 39.91065,
                "PV": {
                    "max_kw": 1000
                },
                "Storage": {
                    "max_kwh": 1000000.0,
                    "max_kw": 10000.0
                },
                "LoadProfile": {
                    "doe_reference_name": "MidriseApartment",
                    "annual_kwh": 100000.0,
                    "year": 2018
                },
                "ElectricTariff": {
                    "blended_monthly_demand_charges_us_dollars_per_kw": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
                    "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
                    "ra_event_day_flags_boolean": event_day_flags,
                    "ra_demand_pricing_us_dollars_per_kw": [18.0]
                },
                "Financial": {
                    "third_party_ownership": False,
                    "offtaker_tax_pct": 0,
                    "offtaker_discount_pct": 0.08,
                    "owner_tax_pct": 0.26,
                    "owner_discount_pct": 0.12
                }
           }
        }
       }

class ResourceAdequacyTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(ResourceAdequacyTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_ra(self):
        """
        Validation run for wind scenario with updated WindToolkit data
        Note no tax, no ITC, no MACRS.
        :return:
        """
        
        d_expected = dict()
        resp = self.get_response(data=ra_post)
        #self.assertHttpCreated(resp)  
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        err_messages = d['messages'].get('error') or []
        if 'Wind Dataset Timed Out' in err_messages:
            print("Wind Dataset Timed Out")
        else:
            c = nested_to_flat(d['outputs'])
            try:
                check_common_outputs(self, c, d_expected)
            except:
                print("Run {} expected outputs may have changed.".format(run_uuid))
                print("Error message: {}".format(d['messages'].get('error')))
                raise
