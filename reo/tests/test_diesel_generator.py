import json
import os
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from reo.models import ModelManager


class GeneratorTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(GeneratorTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def check_common_outputs(self, d_calculated, d_expected):

        c = d_calculated
        e = d_expected

        # check all calculated keys against the expected
        for key, value in e.iteritems():
            tolerance = self.REopt_tol
            if key == 'npv':
                tolerance = 2 * self.REopt_tol

            if key in c and key in e:
                if e[key] == 0:
                    self.assertEqual(c[key], e[key])
                else:
                    self.assertTrue(abs((float(c[key]) - e[key]) / e[key]) < tolerance)

        # Total LCC BAU is sum of utility costs
        self.assertTrue(
            abs((float(c['lcc_bau']) - float(c['total_energy_cost_bau']) - float(c['total_min_charge_adder'])
                 - float(c['total_demand_cost_bau']) - float(c['total_fixed_cost_bau'])) / float(c['lcc_bau']))
            < self.REopt_tol)

    def test_generator_big_enough_for_outage(self):
        """
        Test scenario with interesting rate: high enough demand charges to support battery without PV.
        For this scenario, the diesel generator has enough fuel to meet the critical load during outage.
        :return:
        """
        test_post = os.path.join('reo', 'tests', 'generatorPOST.json')
        nested_data = json.load(open(test_post, 'rb'))
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])

        d_expected = dict()
        d_expected['lcc'] = 228383
        d_expected['npv'] = 894
        d_expected['pv_kw'] = 0
        d_expected['batt_kw'] = 4.25235
        d_expected['batt_kwh'] = 7.76461
        d_expected['fuel_used_gal'] = 1.53

        try:
            self.check_common_outputs(c, d_expected)
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
        d_expected['lcc'] = 245059.0
        d_expected['npv'] = -15955
        d_expected['pv_kw'] = 2.39469
        d_expected['batt_kw'] = 16.6802
        d_expected['batt_kwh'] = 77.8508
        d_expected['fuel_used_gal'] = 25.0

        try:
            self.check_common_outputs(c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise
