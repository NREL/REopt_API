import json
import os
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from reo.models import ModelManager
from reo.utilities import check_common_outputs


class GeneratorTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(GeneratorTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_generator_big_enough_for_outage(self):
        """
        Test scenario with interesting rate: high enough demand charges to support battery without PV.
        For this scenario, the diesel generator has enough fuel to meet the critical load during outage.
        :return:
        """
        test_post = os.path.join('reo', 'tests', 'generatorPOST.json')
        nested_data = json.load(open(test_post, 'rb'))
        nested_data['Scenario']['Site']['LoadProfile']['outage_is_major_event'] = False
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])

        d_expected = dict()
        d_expected['lcc'] = 228519
        d_expected['npv'] = 758
        d_expected['pv_kw'] = 0
        d_expected['batt_kw'] = 2.85178
        d_expected['batt_kwh'] = 4.73317
        d_expected['fuel_used_gal'] = 1.53
        d_expected['avoided_outage_costs_us_dollars'] = 235303.98
        d_expected['microgrid_upgrade_cost_us_dollars'] = 1245.00

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise

    def test_generator_too_small_for_outage(self):
        """
        Test scenario with interesting rate: high enough demand charges to support battery without PV.
        For this scenario, the diesel generator *does not* have enough fuel to meet the critical load during outage.
        :return:
        """
        test_post = os.path.join('reo', 'tests', 'generatorPOST.json')
        nested_data = json.load(open(test_post, 'rb'))
        nested_data['Scenario']['Site']['LoadProfile']['outage_end_hour'] = 40
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])

        d_expected = dict()
        d_expected['lcc'] = 246896.0
        d_expected['npv'] = -17792
        d_expected['pv_kw'] = 4.37636
        d_expected['batt_kw'] = 16.502
        d_expected['batt_kwh'] = 78.3701
        d_expected['fuel_used_gal'] = 25.0
        d_expected['avoided_outage_costs_us_dollars'] = 25277.49
        d_expected['microgrid_upgrade_cost_us_dollars'] = 14420.4

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise
