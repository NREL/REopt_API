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
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class TestLoadBuilder(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestLoadBuilder, self).setUp()
        test_path = os.path.join('load_builder', 'tests')
        self.submit_url = '/v1/load_builder/'
        self.test_path = test_path

    def test_load_builder_endpoint(self):

        # try JSON
        post = json.load(open(os.path.join(self.test_path, 'load_table.json'), 'r'))
        r = self.api_client.post(self.submit_url, format='json', data=post)
        json_resp = json.loads(r.content)
        self.assertEqual(json_resp.keys()[0], 'critical_loads_kw')

        # try CSV
        post = open(os.path.join(self.test_path, 'load_table.csv'), 'r').read()
        r = self.api_client.post(self.submit_url, data=post)
        csv_resp = json.loads(r.content)
        self.assertEqual(csv_resp.keys()[0], 'critical_loads_kw')

        # Check that we get same result
        self.assertEqual(json_resp, csv_resp)