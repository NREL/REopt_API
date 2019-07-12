import json
import os

from reo.models import ModelManager
from tastypie.test import ResourceTestCaseMixin
from unittest import TestCase, skip
from reo.nested_to_flat_output import nested_to_flat
from reo.utilities import check_common_outputs


class WholesaleTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(WholesaleTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_wholesale(self):
        """
        Ensure that for a zero-load site with a excess rate, that REopt allows export above the site load
        :return:
        """
        filepath = os.path.dirname(os.path.abspath(__file__))
        post = json.load(open(os.path.join(filepath, 'posts', 'wholesalePOST.json')))


        # Test 1: wholesale_rate_above_site_load_us_dollars_per_kwh = 0.1
        # Result should be no system, as is not quite profitable.
        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        
        d_expected = dict()
        d_expected['pv_kw'] = 0
        c = nested_to_flat(d['outputs'])

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise

        # Test 2: wholesale_rate_above_site_load_us_dollars_per_kwh = 0.15
        post['Scenario']['Site']['ElectricTariff']['wholesale_rate_above_site_load_us_dollars_per_kwh'] = 0.15
        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        
        d_expected = dict()
        d_expected['pv_kw'] = post['Scenario']['Site']['ElectricTariff']['interconnection_limit_kw']
        d_expected['lcc'] = -54076295428
        d_expected['year_one_energy_produced'] = 138263260000
        d_expected['year_one_export_benefit'] = d_expected['year_one_energy_produced'] * 0.15
        c = nested_to_flat(d['outputs'])