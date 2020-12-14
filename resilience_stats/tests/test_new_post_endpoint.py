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
from reo.nested_to_flat_output import nested_to_flat
from django.test import TestCase
from reo.models import ModelManager
from reo.utilities import check_common_outputs


class OutageSimTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(OutageSimTests, self).setUp()

        # for optimization module
        self.reopt_base_opt = '/v1/job/'
        self.post_opt = os.path.join('resilience_stats', 'tests', 'optPOST.json')
        self.run_uuid = None

        #for simulation module
        self.reopt_base_sim = '/v1/outagesimjob/'


    def get_response_opt(self, data):
        return self.api_client.post(self.reopt_base_opt, format='json', data=data)

    def get_response_sim(self, data_sim):
        return self.api_client.post(self.reopt_base_sim, format='json',
                                    data=data_sim)

    def test_both_modules(self):
        """
        temporary test setup for running an optimizatin problem that precedes the following test for new endpoint for outage simulation module.
        :return:
        """
        data = json.load(open(self.post_opt, 'rb'))
        resp = self.get_response_opt(data)
        self.assertHttpCreated(resp)
        r_opt = json.loads(resp.content)
        run_uuid = r_opt.get('run_uuid')

        assert(run_uuid is not None)
        post_sim = {"run_uuid": run_uuid, "bau": True}
        resp = self.get_response_sim(data_sim=post_sim)
        self.assertHttpCreated(resp)
        r_sim = json.loads(resp.content)
        # print("Response from outagesimjob:", r_sim)
