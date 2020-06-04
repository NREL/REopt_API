import json
from copy import deepcopy
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
from reo.models import ModelManager
import logging
logging.disable(logging.CRITICAL)


post = {"Scenario":
           {"Site": {
                "longitude": -105.2348,
                "latitude": 39.91065,
                "PV": {
                   "max_kw": 1000
               },
               "LoadProfile": {
                   "doe_reference_name": "MidriseApartment",
                   "annual_kwh": 100000.0,
                   "year": 2017
               },
               "ElectricTariff": {
                   "blended_monthly_demand_charges_us_dollars_per_kw": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
                   "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
               },
               "Financial": {
                   "two_party_ownership": False,
                   "offtaker_tax_pct": 0,
                   "offtaker_discount_pct": 0.08,
                   "owner_tax_pct": 0.26,
                   "owner_discount_pct": 0.12
               }
           }
           }
       }


class TwoPartyTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(TwoPartyTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def validate_and_get_outputs(self, post):
        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        return d

    def test_two_party_factor(self):
        two_party_post = deepcopy(post)
        two_party_post['Scenario']['Site']['Financial']['two_party_ownership'] = True

        direct = self.validate_and_get_outputs(post)
        two_party = self.validate_and_get_outputs(two_party_post)

        d = direct['outputs']['Scenario']['Site']['Financial']['lcc_us_dollars']
        t = two_party['outputs']['Scenario']['Site']['Financial']['lcc_us_dollars']

        self.assertTrue(((t - d) - 11976) / 11976 < 0.005,  # less than 0.5% change from expected difference
           msg='Difference between two party and direct ownership LCCs has changed.')
