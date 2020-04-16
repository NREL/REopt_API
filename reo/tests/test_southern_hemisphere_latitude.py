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


class NegativeLatitudeTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(NegativeLatitudeTest, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_southern_hemisphere_latitude(self):
        """
        Tests locations in the Southern Hemisphere where the tilt must be set to the latitude (array type 0 - Ground Mount Fixed (Open Rack)).
        In these cases we need to make the negative latitude positive and set the azimuth to 0.


        :return:
        """

        nested_data = {'Scenario':{
                        'Site': {
                            'latitude':-31.9505,
                            'longitude':115.8605,
                            'ElectricTariff': {'urdb_label':'5b78d2775457a3bf45af0aed'},
                            'LoadProfile': {'doe_reference_name': 'Hospital',
                                            'annual_kwh':12000},
                            'Wind':{'max_kw':0},
                            'PV': {'array_type': 0}
                            }
                        }
                        }

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        messages = d['messages']

        try:
            self.assertEqual(d['inputs']['Scenario']['Site']['PV']['azimuth'], 0,
                             "Not adjusting azimuth for negative latitudes.")

            self.assertEqual(d['inputs']['Scenario']['Site']['PV']['tilt'], 31.9505,
                             "Not adjusting tilt for negative latitudes"
                             )

        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("NegativeLatitudeTest API error message: {}".format(error_msg))
            print("Run uuid: {}".format(d['outputs']['Scenario']['run_uuid']))
            raise e

