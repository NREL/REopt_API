import json
import os
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from resilience_stats.outage_simulator import simulate_outage
from unittest import skip

class TestResilStatsNested(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestResilStatsNested, self).setUp()
        test_path = os.path.join('resilience_stats', 'tests')
        pv_kw_ac_hourly = list()
        
        with open(os.path.join(test_path, 'offline_pv_prod_factor.txt'), 'r') as f:
            for line in f:
                pv_kw_ac_hourly.append(float(line.strip('\n')))

        load = list()
        with open(os.path.join(test_path, 'Load.txt'), 'r') as f:
            for line in f:
                load.append(float(line.strip('\n')))

        stored_energy = list()
        with open(os.path.join(test_path, 'StoredEnergy.txt'), 'r') as f:
            for line in f:
                stored_energy.append(float(line.strip('\n')))

        results = json.loads(open(os.path.join(test_path, 'REopt_results.json')).read())
        pv_kw = results['PVNM']
        batt_kwh = results['Battery Capacity (kWh)']
        batt_kw = results['Battery Power (kW)']
        init_soc = [s / batt_kwh for s in stored_energy]

        self.inputs = {
            'pv_kw': pv_kw,
            'batt_kwh': batt_kwh,
            'batt_kw': batt_kw,
            'pv_kw_ac_hourly': pv_kw_ac_hourly,
            'load': load,
            'init_soc': init_soc,
            'crit_load_factor': 1,
        }
        
        self.url = '/resilience_stats/'

    
    # def test_outage_sim(self):
    #     expected = {
    #         'resilience_hours_min': 0,
    #         'resilience_hours_max': 78,
    #         'resilience_hours_avg': 10.26,
    #         "outage_durations": range(1, 79),
    #         "probs_of_surviving": [0.8486,
    #                                0.7963,
    #                                0.7373,
    #                                0.6624,
    #                                0.59,
    #                                0.5194,
    #                                0.4533,
    #                                0.4007,
    #                                0.3583,
    #                                0.3231,
    #                                0.2934,
    #                                0.2692,
    #                                0.2473,
    #                                0.2298,
    #                                0.2152,
    #                                0.2017,
    #                                0.1901,
    #                                0.1795,
    #                                0.1703,
    #                                0.1618,
    #                                0.1539,
    #                                0.1465,
    #                                0.139,
    #                                0.1322,
    #                                0.126,
    #                                0.1195,
    #                                0.1134,
    #                                0.1076,
    #                                0.1024,
    #                                0.0979,
    #                                0.0938,
    #                                0.0898,
    #                                0.0858,
    #                                0.0818,
    #                                0.0779,
    #                                0.0739,
    #                                0.0699,
    #                                0.066,
    #                                0.0619,
    #                                0.0572,
    #                                0.0524,
    #                                0.0477,
    #                                0.0429,
    #                                0.038,
    #                                0.0331,
    #                                0.0282,
    #                                0.0233,
    #                                0.0184,
    #                                0.015,
    #                                0.012,
    #                                0.0099,
    #                                0.0083,
    #                                0.0073,
    #                                0.0068,
    #                                0.0064,
    #                                0.0062,
    #                                0.0059,
    #                                0.0057,
    #                                0.0055,
    #                                0.0053,
    #                                0.005,
    #                                0.0048,
    #                                0.0046,
    #                                0.0043,
    #                                0.0041,
    #                                0.0037,
    #                                0.0032,
    #                                0.0027,
    #                                0.0023,
    #                                0.0018,
    #                                0.0014,
    #                                0.0009,
    #                                0.0007,
    #                                0.0006,
    #                                0.0005,
    #                                0.0003,
    #                                0.0002,
    #                                0.0001],
    #     }
    #     resp = simulate_outage(**self.inputs)

    #     self.assertAlmostEqual(expected['resilience_hours_min'], resp['resilience_hours_min'], places=3)
    #     self.assertAlmostEqual(expected['resilience_hours_max'], resp['resilience_hours_max'], places=3)
    #     self.assertAlmostEqual(expected['resilience_hours_avg'], resp['resilience_hours_avg'], places=3)
    #     self.assertAlmostEqual(expected['outage_durations'], resp['outage_durations'], places=3)
    #     for x, y in zip(expected['probs_of_surviving'], resp['probs_of_surviving']):
    #         self.assertAlmostEquals(x, y, places=3)

    def test_no_resilience(self):
        self.inputs.update(pv_kw=0, batt_kw=0)

        resp = simulate_outage(**self.inputs)

        self.assertEqual(0, resp['resilience_hours_min'])
        self.assertEqual(0, resp['resilience_hours_max'])
        self.assertEqual(0, resp['resilience_hours_avg'])
        self.assertEqual(None, resp['outage_durations'])
        self.assertEqual(None, resp['probs_of_surviving'])

    @skip("Will Fail Until Workflow Complete")
    def test_resil_endpoint_nested(self):
        post = json.load(open(os.path.join('tests', 'POST_nested.json'), 'r'))
        r = self.api_client.post('/api/v1/reopt/', format='json', data=post)
        reopt_resp = json.loads(r.content)
        data = {'run_uuid': reopt_resp['uuid']}
        resp = self.api_client.get(self.url, format='json', data=data)
        self.assertEqual(resp.status_code, 200)

        resp_dict = json.loads(resp.content)
        
        self.assertEqual(resp_dict["probs_of_surviving"], [0.0114, 0.0027])
        self.assertEqual(resp_dict["resilience_hours_avg"], 0.01)
        self.assertEqual(resp_dict["outage_durations"], [1,2])
        self.assertEqual(resp_dict["resilience_hours_min"], 0)
        self.assertEqual(resp_dict["resilience_hours_max"], 2)




