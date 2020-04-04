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
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from unittest import skip
from reo.models import ModelManager
from reo.utilities import check_common_outputs
from reo.validators import ValidateNestedInput
import logging
logging.disable(logging.CRITICAL)

case_studies = {'PV':'76168a37-a78b-4ef3-bdb8-a2f8b213430b',
                'PV2':'10c625b8-35b4-4b98-a01f-f4dc5732983c',
                'PV3':'ebfc3ee6-42d6-4a70-accb-15908e8ac2bf',
                'wind':'eda919d6-1481-4bf9-a531-a1b3397c8c67',
                'storage':'2721ed09-7cdb-4d08-a690-28ca30eb6a6f',
                'PV + storage':'8ff29780-4e1b-4aca-b079-1342ea21bde2',
                'PV + storage + wind':'c8d51686-b991-43cd-bab7-68e03f8872d1',
                'PV + wind':'b5e895b8-a851-49c0-9650-2072408d1b89',
                'storage + wind':'7605344c-964c-4e17-9c14-688d6e9fbfb6',
                'tiered PV':'5b75684a-232d-4e95-8bf1-3fcb47b07a46',
                'tiered PV + BESS':'dc647e7a-be89-4044-ab40-e500a5f90e6b',
                'TOU PV':'02bd7144-c484-4e42-b7e4-9ea077bfbc34',
                'TOU PV + BESS':'6c15335f-4d77-4ade-a6f8-a4fd486488d1',
                'PV + storage + MCA':'5725f8a4-a3a1-4f5b-ac97-491718929be5',
                'TOU PV + LBM':'dc52957d-a857-46cb-ad4c-989889c0592d',
                'wind + Monthly Demand':'0cadae26-104a-4dad-a212-d0843a8cc4db'}


class CaseStudyTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(CaseStudyTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)
    def get_case_study_inputs(self, case_study):
        case_study_inputs_path = './reo/tests/case_studies/Run{}/Inputs/POST.json'.format(case_study)
        inputs = json.load(open(case_study_inputs_path))
        del inputs['Scenario']['Site']['Generator']['size_kw']
        return inputs

    def get_case_study_results(self, case_study):
        case_study_results_path = './reo/tests/case_studies/Run{}/Outputs/REopt_results.json'.format(case_study)
        return json.load(open(case_study_results_path))

    def run_study(self, study):

        # Aquire JSON of test case
        study = case_studies[study]
        inputs = self.get_case_study_inputs(study)

        # Post job, validate https code
        resp = self.get_response(data=inputs)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)

        # Get results from the database
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Create objects to be checked
        #results = self.get_case_study_results(study)
        #d_expected['lcc'] = results['lcc']

        expected = 437716.0
        return nested_to_flat(d['outputs'])

    def test_PV(self):
        c = self.run_study('PV')
        expected = 437716.0
        self.assertAlmostEqual(c['lcc'], expected, places=2, msg="LCC doesn't match test case results")

    def test_wind(self):
        c = self.run_study('wind')
        expected = 437716.0
        print(c['lcc'])
        #self.assertAlmostEqual(c['lcc'], expected, places=2, msg="LCC doesn't match test case results")

    def test_PV_storage(self):
        c = self.run_study('PV + storage')
        expected = 437716.0
        print(c['lcc'])
        #self.assertAlmostEqual(c['lcc'], expected, places=2, msg="LCC doesn't match test case results")

    def test_PV(self):
        c = self.run_study('PV')
        expected = 437716.0
        print(c['lcc'])
        #self.assertAlmostEqual(c['lcc'], expected, places=2, msg="LCC doesn't match test case results")

    def test_PV(self):
        c = self.run_study('PV')
        expected = 437716.0
        print(c['lcc'])
        #self.assertAlmostEqual(c['lcc'], expected, places=2, msg="LCC doesn't match test case results")

    def test_PV(self):
        c = self.run_study('PV')
        expected = 437716.0
        print(c['lcc'])
        #self.assertAlmostEqual(c['lcc'], expected, places=2, msg="LCC doesn't match test case results")

    def test_PV(self):
        c = self.run_study('PV')
        expected = 437716.0
        print(c['lcc'])
        #self.assertAlmostEqual(c['lcc'], expected, places=2, msg="LCC doesn't match test case results")

