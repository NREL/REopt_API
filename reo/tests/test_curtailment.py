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


class WindTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(WindTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_pv_curtailment(self):
        """
        Validation run for wind scenario with updated WindToolkit data
        Note no tax, no ITC, no MACRS.
        :return:
        """
        post_path = os.path.join('reo', 'tests', 'posts', 'test_curtailment_POST.json')
        with open(post_path, 'r') as fp:
            test_post = json.load(fp)
        d_expected = dict()
        d_expected['lcc'] = 5908025
        d_expected['npv'] = -4961719
        d_expected['average_annual_energy_curtailed_pv'] = 1015235
        d_expected['average_annual_energy_curtailed_wind'] = 2422069
        resp = self.get_response(data=test_post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        err_messages = d['messages'].get('error') or []
        if 'Wind Dataset Timed Out' in err_messages:
            print("Wind Dataset Timed Out")
        else:
            c = nested_to_flat(d['outputs'])
            print(d['outputs']['Scenario']['Site'].keys())
            c['average_annual_energy_curtailed_pv'] = sum(d['outputs']['Scenario']['Site']['PV'][
                                                               'year_one_curtailed_production_series_kw'])
            c['average_annual_energy_curtailed_wind'] = sum(d['outputs']['Scenario']['Site']['Wind'][
                                                               'year_one_curtailed_production_series_kw'])
            try:
                check_common_outputs(self, c, d_expected)
            except:
                print("Run {} expected outputs may have changed.".format(run_uuid))
                print("Error message: {}".format(d['messages'].get('error')))
                raise
