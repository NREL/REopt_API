import json
from copy import deepcopy
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat
from unittest import TestCase
from reo.models import ModelManager
from reo.utilities import check_common_outputs
import logging
logging.disable(logging.CRITICAL)


post = {"Scenario":
           {"Site": {
                "latitude": 30.382,
                "longitude": -97.7218,
                "PV": {
                   "max_kw": 0
               },
               "LoadProfile": {
                   "doe_reference_name": "LargeHotel",
                   "annual_kwh": 1000000.0
               },
               "ElectricTariff": {
                   "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                   "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
               },
               "Financial": {
                   "two_party_ownership": False,
                   "offtaker_discount_pct": 0.083,
                   "om_cost_escalation_pct": 0.006,
                   "escalation_pct": 0.006
               #    "owner_tax_pct": 0.1,
               #    "owner_discount_pct": 0.09
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

        import ipdb; ipdb.set_trace()

        msg = 'Direct ownership and two_part ownership have the same results.'
        self.assertNotEqual(d, t, msg=msg)
