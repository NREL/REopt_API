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
import tzlocal
import json
import datetime
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


def now():
    return tzlocal.get_localzone().localize(datetime.datetime.now())


class CashFlowTest(ResourceTestCaseMixin, TestCase):
    """
    These tests just ensure that input cells in Proforma are filled in with the appropriate values.
    Unfortunately, we cannot automatically validate calculated values in the spreadsheet. So, the only way to truely
    validate the Proforma is to visually compare the Proforma LCC's and NPV against the API's results.

    200415 nlaws: removing the tests for input cells vs. database. No reason to maintain these tests now that the
    proforma rows are created dynamically in the proforma_generator. As mentioned above, the only way to test the
    proforma is visually comparing the NPV, LCC's, etc. between the API response and the Excel workbook.
    """

    REopt_tol = 5e-5

    def setUp(self):
        super(CashFlowTest, self).setUp()
        self.example_reopt_request_data = json.loads(open('proforma/tests/test_data.json').read())
        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.proforma_url = '/v1/job/<run_uuid>/proforma/'

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        uuid = json.loads(initial_post.content)['run_uuid']
        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
        return response

    def test_bad_run_uuid(self):
        run_uuid = "5"
        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(run_uuid))).content)
        # status = response['outputs']['Scenario']['status']
        self.assertDictEqual(response,
                             {u'outputs': {u'Scenario': {u'status': u'error'}},
                              u'messages': {u'error': u'badly formed hexadecimal UUID string'}})