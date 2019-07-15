import json
import os
import uuid
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from resilience_stats.outage_simulator_LF import simulate_outage


class TestResilStats(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestResilStats, self).setUp()
        self.test_path = os.path.join('resilience_stats', 'tests')

        def readFiles(path):
            test_path = os.path.join('resilience_stats', 'tests', path)
            results = json.loads(open(os.path.join(test_path, 'REopt_results.json')).read())
            pv_kw = results['PVNM']
            pv_kw_ac_hourly = list()
            
            with open(os.path.join(test_path, 'offline_pv_prod_factor.txt'), 'r') as f:
                for line in f:
                    pv_kw_ac_hourly.append(pv_kw * float(line.strip('\n')))

            timesteps_per_hr = len(pv_kw_ac_hourly) / 8760

            load = list()
            with open(os.path.join(test_path, 'Load.txt'), 'r') as f:
                for line in f:
                    load.append(float(line.strip('\n')))
            
            stored_energy = list()
            with open(os.path.join(test_path, 'StoredEnergy.txt'), 'r') as f:
                for line in f:
                    stored_energy.append(float(line.strip('\n'))*timesteps_per_hr)

            batt_kwh = results['Battery Capacity (kWh)']
            batt_kw = results['Battery Power (kW)']
            init_soc = [s / batt_kwh for s in stored_energy]

            inputDict = {
                'batt_kwh': batt_kwh,
                'batt_kw': batt_kw,
                'pv_kw_ac_hourly': pv_kw_ac_hourly,
                'wind_kw_ac_hourly': [],
                'critical_loads_kw': load,
                'init_soc': init_soc,
                'diesel_kw': 200,
                'fuel_available': 200,
                'm': 0.0648,
                'b': 0.0067,
            }

            return inputDict

        inputDict = readFiles('')
        inputDict1 = readFiles('timestep_1')
        inputDict2 = readFiles('timestep_2')

        self.inputs = inputDict
        self.inputs1 = inputDict1
        self.inputs2 = inputDict2

        # self.test_path = test_path
        
        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/resilience_stats/'
        

    def test_outage_sim_no_diesel(self):
        """
        For the case that no diesel generator is on site, outage simulation with load following strategy should have the
        same results as existing simulation's results.
        """
        inputs = self.inputs
        inputs.update(diesel_kw=0, fuel_available=0, m=0, b=0)

        # Output parse from existing simulation
        expected = {
            'resilience_hours_min': 0,
            'resilience_hours_max': 78,
            'resilience_hours_avg': 10.26,
            "outage_durations": range(1, 79),
            "probs_of_surviving": [],
        }
        resp = simulate_outage(**inputs)

        self.assertAlmostEqual(expected['resilience_hours_min'], resp['resilience_hours_min'], places=3)
        self.assertAlmostEqual(expected['resilience_hours_max'], resp['resilience_hours_max'], places=3)
        self.assertAlmostEqual(expected['resilience_hours_avg'], resp['resilience_hours_avg'], places=3)
        self.assertAlmostEqual(expected['outage_durations'], resp['outage_durations'], places=3)
        for x, y in zip(expected['probs_of_surviving'], resp['probs_of_surviving']):
            self.assertAlmostEquals(x, y, places=3)

    def test_outage_sim(self):
        """
        With diesel + PV + storage
        """
        expected = {
            'resilience_hours_min': 28,
            'resilience_hours_max': 145,
            'resilience_hours_avg': 69.63,
            "outage_durations": range(1, 146),
            "probs_of_surviving": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                  1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9998, 0.9993, 0.9987, 0.9971,
                                  0.9955, 0.9943, 0.993, 0.991, 0.9888, 0.9844, 0.9792, 0.9729, 0.9664, 0.9583, 0.9494,
                                  0.94, 0.9298, 0.9189, 0.905, 0.8926, 0.8755, 0.8588, 0.842, 0.8233, 0.8031, 0.7834,
                                  0.7639, 0.7449, 0.7264, 0.7082, 0.692, 0.6737, 0.6543, 0.6363, 0.6182, 0.5983, 0.5782,
                                  0.5583, 0.537, 0.5159, 0.4952, 0.4749, 0.4533, 0.4322, 0.4116, 0.3925, 0.3752, 0.3579,
                                  0.3402, 0.3224, 0.3049, 0.2884, 0.2721, 0.2562, 0.2403, 0.2243, 0.2088, 0.1949, 0.1813,
                                  0.1683, 0.1559, 0.1443, 0.1333, 0.1228, 0.1129, 0.1037, 0.0959, 0.0886, 0.0821, 0.0766,
                                  0.0716, 0.0668, 0.0621, 0.0575, 0.0531, 0.0486, 0.0442, 0.04, 0.0357, 0.032, 0.0284,
                                  0.0252, 0.0229, 0.021, 0.0193, 0.0177, 0.0161, 0.0145, 0.0129, 0.0113, 0.0097, 0.0082,
                                  0.0068, 0.0057, 0.0049, 0.0043, 0.0038, 0.0034, 0.0031, 0.0027, 0.0024, 0.0021, 0.0018,
                                  0.0016, 0.0015, 0.0014, 0.0013, 0.0011, 0.001, 0.0009, 0.0008, 0.0007, 0.0006, 0.0005,
                                  0.0003, 0.0002, 0.0001]
        }
        resp = simulate_outage(**self.inputs)

        self.assertAlmostEqual(expected['resilience_hours_min'], resp['resilience_hours_min'], places=3)
        self.assertAlmostEqual(expected['resilience_hours_max'], resp['resilience_hours_max'], places=3)
        self.assertAlmostEqual(expected['resilience_hours_avg'], resp['resilience_hours_avg'], places=3)
        self.assertAlmostEqual(expected['outage_durations'], resp['outage_durations'], places=3)
        for x, y in zip(expected['probs_of_surviving'], resp['probs_of_surviving']):
            self.assertAlmostEquals(x, y, places=3)

    def test_no_resilience(self):
        inputs = self.inputs
        inputs.update(pv_kw_ac_hourly=[], batt_kw=0, diesel_kw=0)
        resp = simulate_outage(**inputs)

        self.assertEqual(0, resp['resilience_hours_min'])
        self.assertEqual(0, resp['resilience_hours_max'])
        self.assertEqual(0, resp['resilience_hours_avg'])
        self.assertEqual(None, resp['outage_durations'])
        self.assertEqual(None, resp['probs_of_surviving'])
        self.assertEqual(None, resp['probs_of_surviving_by_month'])
        self.assertEqual(None, resp['probs_of_surviving_by_hour_of_the_day'])
        
    def test_flexible_timesteps(self):
        """
        Same input with different timesteps-per-hour should have almost equal results.
        """
        resp1 = simulate_outage(**self.inputs1)
        resp2 = simulate_outage(**self.inputs2)

        self.assertAlmostEqual(1, resp2['resilience_hours_max'] / resp1['resilience_hours_max'], places=1)
        self.assertAlmostEqual(1, resp2['resilience_hours_min'] / resp1['resilience_hours_min'], places=1)
        self.assertAlmostEqual(1, resp2['resilience_hours_avg'] / resp1['resilience_hours_avg'], places=1)

        for x, y in zip(resp1['probs_of_surviving'], resp2['probs_of_surviving']):
            self.assertAlmostEquals(x, y, places=1)

    def test_resil_endpoint(self):
        post = json.load(open(os.path.join(self.test_path, 'POST_nested.json'), 'r'))
        r = self.api_client.post(self.submit_url, format='json', data=post)
        reopt_resp = json.loads(r.content)
        uuid = reopt_resp['run_uuid']

        for _ in range(2):
            resp = self.api_client.get(self.results_url.replace('<run_uuid>', uuid))
            self.assertEqual(resp.status_code, 200)

            resp_dict = json.loads(resp.content)

            expected_probs = [0.605, 0.2454, 0.1998, 0.1596, 0.1237, 0.0897, 0.0587, 0.0338, 0.0158, 0.0078, 0.0038,
                              0.0011]
            for idx, p in enumerate(resp_dict["probs_of_surviving"]):
                self.assertAlmostEqual(p, expected_probs[idx], places=2)
            self.assertEqual(resp_dict["resilience_hours_avg"], 1.54)
            self.assertEqual(resp_dict["outage_durations"], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            self.assertEqual(resp_dict["resilience_hours_min"], 0)
            self.assertEqual(resp_dict["resilience_hours_max"], 12)