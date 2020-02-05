import json
import os
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat
from unittest import TestCase
from reo.models import ModelManager
from reo.utilities import check_common_outputs


class CriticalLoadBAUTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(CriticalLoadBAUTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_critical_load_bau_cannot_sustain_outage(self):
        """
        Test scenario with
        - outage_start_hour: 16
        - outage_end_hour: 30
        - existing diesel generator 20 kW
        - existing PV 3 kW
        - available fuel 5 gallons
        .
        :return:
        """
        test_post = os.path.join('reo', 'tests', 'posts', 'critical_load_bau_cannot_sustain_outage.json')
        nested_data = json.load(open(test_post, 'rb'))

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])
        load_bau = d['outputs']['Scenario']['Site']['LoadProfile']['year_one_electric_load_series_kw']

        # check first 100 hours
        c['load_bau'] = load_bau[:100]
        c['status'] = d['outputs']['Scenario']['status']
        c['resilience_check_flag'] = d['outputs']['Scenario']['Site']['LoadProfile']['resilience_check_flag']
        c['sustain_hours'] = d['outputs']['Scenario']['Site']['LoadProfile']['sustain_hours']

        load_bau_expected = [19.5635, 18.9651, 20.3557, 19.0925, 20.2735, 19.0383, 20.3317, 13.6065, 9.20435, 7.3294,
                             7.14286, 5.62887, 5.20491, 4.40816, 4.21774, 4.21774, 2.13005, 6.20206, 8.43682, 8.63245,
                             8.89582, 8.97923, 9.34905, 9.36905, 0, 0, 0, 0, 0, 0, 24.4053, 32.5911, 39.7653, 47.1892,
                             47.1892, 47.1892, 42.9714, 47.1892, 47.1892, 47.1892, 47.1892, 21.2452, 16.5046, 17.0414,
                             17.6651, 17.7595, 18.298, 18.2451, 18.8185, 18.7475, 19.4191, 19.1492, 19.881, 19.5412,
                             24.4053, 32.5911, 39.7653, 47.1892, 47.1892, 47.1892, 42.9714, 47.1892, 47.1892, 47.1892,
                             47.1892, 21.4645, 16.1414, 16.5509, 16.7304, 17.308, 17.3808, 17.858, 17.8368, 18.1468,
                             17.8958, 18.1091, 17.7883, 18.1495, 24.4053, 32.5911, 39.7653, 47.1892, 47.1892, 47.1892,
                             42.9714, 47.1892, 47.1892, 47.1892, 47.1892, 20.9702, 15.1757, 15.3862, 15.8559, 15.9813,
                             16.7046, 16.5464, 17.2186, 16.8851, 17.7358, 17.2112]

        d_expected = dict()
        d_expected['load_bau'] = load_bau_expected
        d_expected['status'] = 'optimal'
        d_expected['total_energy_cost_bau'] = 53890.95
        d_expected['year_one_energy_cost_bau'] = 7429.26
        d_expected['resilience_check_flag'] = False
        d_expected['sustain_hours'] = 8

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise

    def test_critical_load_bau_can_sustain_outage(self):
        """
        Test scenario with
        - outage_start_hour: 16
        - outage_end_hour: 20
        - existing diesel generator 20 kW
        - existing PV 3 kW
        - available fuel 50 gallons
        """
        test_post = os.path.join('reo', 'tests', 'posts', 'critical_load_bau_can_sustain_outage.json')
        nested_data = json.load(open(test_post, 'rb'))

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])
        load_bau = d['outputs']['Scenario']['Site']['LoadProfile']['year_one_electric_load_series_kw']

        # check first 100 hours
        c['load_bau'] = load_bau[:100]
        c['status'] = d['outputs']['Scenario']['status']
        c['resilience_check_flag'] = d['outputs']['Scenario']['Site']['LoadProfile']['resilience_check_flag']
        c['sustain_hours'] = d['outputs']['Scenario']['Site']['LoadProfile']['sustain_hours']

        load_bau_expected = [19.5635, 18.9651, 20.3557, 19.0925, 20.2735, 19.0383, 20.3317, 13.6065, 9.20435, 7.3294,
                             7.14286, 5.62887, 5.20491, 4.40816, 4.21774, 4.21774, 2.13005, 6.20206, 8.43682, 8.63245,
                             17.7916, 17.9585, 18.6981, 18.7381, 19.5483, 19.2944, 20.0656, 19.5757, 20.2466, 19.8914,
                             24.4053, 32.5911, 39.7653, 47.1892, 47.1892, 47.1892, 42.9714, 47.1892, 47.1892, 47.1892,
                             47.1892, 21.2452, 16.5046, 17.0414, 17.6651, 17.7595, 18.298, 18.2451, 18.8185, 18.7475,
                             19.4191, 19.1492, 19.881, 19.5412, 24.4053, 32.5911, 39.7653, 47.1892, 47.1892, 47.1892,
                             42.9714, 47.1892, 47.1892, 47.1892, 47.1892, 21.4645, 16.1414, 16.5509, 16.7304, 17.308,
                             17.3808, 17.858, 17.8368, 18.1468, 17.8958, 18.1091, 17.7883, 18.1495, 24.4053, 32.5911,
                             39.7653, 47.1892, 47.1892, 47.1892, 42.9714, 47.1892, 47.1892, 47.1892, 47.1892, 20.9702,
                             15.1757, 15.3862, 15.8559, 15.9813, 16.7046, 16.5464, 17.2186, 16.8851, 17.7358, 17.2112]

        d_expected = dict()
        d_expected['load_bau'] = load_bau_expected
        d_expected['status'] = 'optimal'
        d_expected['total_energy_cost_bau'] = 54201.86
        d_expected['year_one_energy_cost_bau'] = 7472.12
        d_expected['resilience_check_flag'] = True
        d_expected['sustain_hours'] = 4

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise
