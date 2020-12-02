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
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
import json
import uuid
import logging
logging.disable(logging.CRITICAL)


class SummaryResourceTest(ResourceTestCaseMixin, TestCase):

    # mimic user passing in info
    def setUp(self):
        super(SummaryResourceTest, self).setUp()
        self.reopt_base_job_url = '/v1/job/'
        self.summary_url = '/v1/user/{}/summary'
        self.unlink_url = '/v1/user/{}/unlink/{}'
        self.test_user_uuid = '501d1dd9-9779-470b-a631-01c5fbdee570'
        self.test_alt_user_uuid = '701d1dd9-9779-470b-a631-01c5fbdee570'
        self.test_run_uuid = None

    def test_summary_and_unlink(self):
        self.test_run_uuid = self.send_valid_nested_post(self.test_user_uuid)
        summary_response = self.get_summary()
        self.assertTrue(self.test_run_uuid in str(summary_response.content))
        self.unlink_record()
        self.unlink_messages()

    def unlink_record(self):
        unlink_response = self.get_unlink(self.test_user_uuid, self.test_run_uuid)
        self.assertTrue(unlink_response.status_code==204)
        summary_response = self.get_summary()
        self.assertFalse(self.test_run_uuid in str(summary_response.content))

    def unlink_messages(self):

      bad_uuid = str(uuid.uuid4())
      unlink_response = self.get_unlink(bad_uuid, self.test_run_uuid)
      self.assertTrue("User {} does not exist".format(bad_uuid) in str(unlink_response.content))

      unlink_response = self.get_unlink(self.test_user_uuid, bad_uuid)
      self.assertTrue("Run {} does not exist".format(bad_uuid) in str(unlink_response.content))

      test_alt_run_uuid = self.send_valid_nested_post(self.test_alt_user_uuid)
      unlink_response = self.get_unlink(self.test_user_uuid, test_alt_run_uuid)
      self.assertTrue("Run {} is not associated with user {}".format(test_alt_run_uuid, self.test_user_uuid))

    def get_unlink(self,user_uuid, run_uuid):
        return self.api_client.get(self.unlink_url.format(user_uuid, run_uuid))

    def get_summary(self):
        return self.api_client.get(self.summary_url.format(self.test_user_uuid))

    def post_job(self, data):
        return self.api_client.post(self.reopt_base_job_url, format='json', data=data)

    def send_valid_nested_post(self,user_uuid):


        flat_data = {"roof_area": 5000.0, "batt_can_gridcharge": True, "load_profile_name": "RetailStore", "pv_macrs_schedule": 5, "load_size": 100.0, "longitude": -118.1164613,
                     "pv_macrs_bonus_fraction": 0.4, "batt_macrs_bonus_fraction": 0.4, "offtaker_tax_rate": 0.4,
                     "batt_macrs_schedule": 5, "latitude": 34.5794343, "module_type": 1, "array_type": 1, "tilt": 34.5794343, "land_area": 1.0, "crit_load_factor": 1.0, "blended_utility_rate":[0 for _ in range(0,12)], "demand_charge":[0 for _ in range(0,12)], "wind_kw_max":0,
                     "urdb_rate": {"sector": "Commercial", "peakkwcapacitymax": 200, "energyweekdayschedule": [[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[2,2,2,2,2,2,2,2,3,3,3,3,4,4,4,4,4,4,3,3,3,3,3,2],[2,2,2,2,2,2,2,2,3,3,3,3,4,4,4,4,4,4,3,3,3,3,3,2],[2,2,2,2,2,2,2,2,3,3,3,3,4,4,4,4,4,4,3,3,3,3,3,2],[2,2,2,2,2,2,2,2,3,3,3,3,4,4,4,4,4,4,3,3,3,3,3,2],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0]], "demandattrs": [{"Facilties Voltage Discount (2KV-<50KV)": "$-0.18/KW"},{"Facilties Voltage Discount >50 kV-<220kV": "$-5.78/KW"},{"Facilties Voltage Discount >220 kV": "$-9.96/KW"},{"Time Voltage Discount (2KV-<50KV)": "$-0.70/KW"},{"Time Voltage Discount >50 kV-<220kV": "$-1.93/KW"},{"Time Voltage Discount >220 kV": "$-1.95/KW"}], "energyratestructure": [[{"rate": 0.0712, "unit": "kWh"}],[{"rate": 0.09368, "unit": "kWh"}],[{"rate": 0.066, "unit": "kWh"}],[{"rate": 0.08888, "unit": "kWh"}],[{"rate": 0.1355, "unit": "kWh"}]], "energyweekendschedule": [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], "demandweekendschedule": [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], "utility": "Southern California Edison Co", "flatdemandstructure": [[{"rate": 13.2}]], "startdate": 1433116800, "phasewiring": "Single Phase", "source": "http://www.sce.com/NR/sc3/tm2/pdf/ce30-12.pdf", "label": "55fc81d7682bea28da64f9ae", "flatdemandunit": "kW", "eiaid": 17609, "voltagecategory": "Primary", "revisions": [1433408708,1433409358,1433516188,1441198316,1441199318,1441199417,1441199824,1441199996,1454521683], "demandweekdayschedule": [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,0],[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,0],[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,0],[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], "voltageminimum": 2000, "description": "- Energy tiered charge = generation charge + delivery charge\r\n\r\n- Time of day demand charges (generation-based) are to be added to the monthly demand charge(Delivery based).", "energyattrs": [{"Voltage Discount (2KV-<50KV)": "$-0.00106/Kwh"},{"Voltage Discount (>50 KV<220 KV)": "$-0.00238/Kwh"},{"Voltage Discount at 220 KV": "$-0.0024/Kwh"},{"California Climate credit": "$-0.00669/kwh"}], "demandrateunit": "kW", "flatdemandmonths": [0,0,0,0,0,0,0,0,0,0,0,0], "approved": True, "fixedmonthlycharge": 259.2, "enddate": 1451520000, "name": "Time of Use, General Service, Demand Metered, Option B: GS-2 TOU B, Single Phase", "country": "USA", "uri": "http://en.openei.org/apps/IURDB/rate/view/55fc81d7682bea28da64f9ae", "voltagemaximum": 50000, "peakkwcapacitymin": 20, "peakkwcapacityhistory": 12, "demandratestructure": [[{"rate": 0}],[{"rate": 5.3}],[{"rate": 18.11}]]}}

        nested_data = {'Scenario':{
                        'Site': {
                            'latitude':-31.9505,
                            'longitude':115.8605,
                            'ElectricTariff':
                                {"blended_annual_rates_us_dollars_per_kwh": 0.10,
                                 "blended_annual_demand_charges_us_dollars_per_kw": 0},
                            'LoadProfile': {'doe_reference_name': 'Hospital',
                                            'annual_kwh':100},
                            'Wind': {'max_kw':0},
                            'PV': {'max_kw': 0},
                            'Storage': {'max_kw': 0}
                            }
                        }}
        nested_data['Scenario']['user_uuid'] = user_uuid
        resp = self.post_job(data=nested_data)
        r = json.loads(resp.content)
        return r.get('run_uuid')
