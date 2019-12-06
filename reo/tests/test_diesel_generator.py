import json
import os
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
from reo.nested_to_flat_output import nested_to_flat
#from unittest import TestCase
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
        test_post = os.path.join('reo', 'tests', 'posts', 'generatorPOST.json')
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
        # The expected fuel consumption of the geneartor for this test case has changed with the "diesel generator
        # sizing" capability additon. This is because the generator is now allowing to charge the battery as well.
        # So, for hour 11 and 12 (when outage happens), generator is now charging battery with 3.00845 and 0.986111 kWh,
        # along with serving the load, Thereby increasing its fuel consumption.
        d_expected['fuel_used_gal'] = 1.79 # 1.53
        d_expected['avoided_outage_costs_us_dollars'] = 472773.94
        d_expected['microgrid_upgrade_cost_us_dollars'] = 1245.00

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise

        critical_load = d['outputs']['Scenario']['Site']['LoadProfile']['critical_load_series_kw']
        generator_to_load = d['outputs']['Scenario']['Site']['Generator']['year_one_to_load_series_kw']
        outage_start = d['inputs']['Scenario']['Site']['LoadProfile']['outage_start_hour']
        outage_end = d['inputs']['Scenario']['Site']['LoadProfile']['outage_end_hour']

        for x, y in zip(critical_load[outage_start:outage_end], generator_to_load[outage_start:outage_end]):
            self.assertAlmostEquals(x, y, places=3)

    def test_generator_too_small_for_outage(self):
        """
        Test scenario with interesting rate: high enough demand charges to support battery without PV.
        For this scenario, the diesel generator *does not* have enough fuel to meet the critical load during outage.
        :return:
        """
        test_post = os.path.join('reo', 'tests', 'posts', 'generatorPOST_part2.json')
        nested_data = json.load(open(test_post, 'rb'))
        nested_data['Scenario']['Site']['LoadProfile']['outage_end_hour'] = 64
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)        
        c = nested_to_flat(d['outputs'])

        d_expected = dict()
        d_expected['lcc'] = 768489.0
        d_expected['npv'] = 217226.0
        d_expected['pv_kw'] = 215.1007
        d_expected['batt_kw'] = 39.7699
        d_expected['batt_kwh'] = 269.1067
        d_expected['fuel_used_gal'] = 2.0
        d_expected['microgrid_upgrade_cost_us_dollars'] = 97291.8
        """
        the expected value for 'avoided_outage_costs_us_dollars' is commented out
        because after upgrade to Python 3 the values were different on Mac and Linux platform.
        value on Mac:
        d_expected['avoided_outage_costs_us_dollars'] = 174130.09
        
        value on Linux:        
        d_expected['avoided_outage_costs_us_dollars'] = 171850.07 
        """


        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise
