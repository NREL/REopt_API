import json
import os
import uuid
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from resilience_stats.outage_simulator_LF import simulate_outage
import time
from unittest import skip

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
                    stored_energy.append(float(line.strip('\n')) * timesteps_per_hr)

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
            "probs_of_surviving": [0.8486, 0.7963, 0.7373, 0.6624, 0.59, 0.5194, 0.4533, 0.4007, 0.3583, 0.3231, 0.2934,
                                   0.2692, 0.2473, 0.2298, 0.2152, 0.2017, 0.1901, 0.1795, 0.1703, 0.1618, 0.1539,
                                   0.1465, 0.139, 0.1322, 0.126, 0.1195, 0.1134, 0.1076, 0.1024, 0.0979, 0.0938, 0.0898,
                                   0.0858, 0.0818, 0.0779, 0.0739, 0.0699, 0.066, 0.0619, 0.0572, 0.0524, 0.0477,
                                   0.0429, 0.038, 0.0331, 0.0282, 0.0233, 0.0184, 0.015, 0.012, 0.0099, 0.0083, 0.0073,
                                   0.0068, 0.0064, 0.0062, 0.0059, 0.0057, 0.0055, 0.0053, 0.005, 0.0048, 0.0046,
                                   0.0043, 0.0041, 0.0037, 0.0032, 0.0027, 0.0023, 0.0018, 0.0014, 0.0009, 0.0007,
                                   0.0006, 0.0005, 0.0003, 0.0002, 0.0001]
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
            'resilience_hours_min': 0,
            'resilience_hours_max': 145,
            'resilience_hours_avg': 69.11,
            "outage_durations": range(1, 146),
            "probs_of_surviving": [0.9986, 0.9976, 0.9967, 0.9959, 0.9952, 0.9945, 0.9938, 0.9932, 0.9927, 0.9925,
                                   0.9925, 0.9925, 0.9925, 0.9925, 0.9925, 0.9925, 0.9925, 0.9925, 0.9925, 0.9925,
                                   0.9925, 0.9925, 0.9925, 0.9925, 0.9925, 0.9925, 0.9925, 0.9925, 0.9922, 0.9918,
                                   0.9912, 0.9896, 0.988, 0.9868, 0.9855, 0.9834, 0.9813, 0.9768, 0.9717, 0.9654,
                                   0.9589, 0.9508, 0.9419, 0.9324, 0.9223, 0.9114, 0.8975, 0.885, 0.8679, 0.8513,
                                   0.8345, 0.8158, 0.7955, 0.7759, 0.7564, 0.7373, 0.7188, 0.7007, 0.6845, 0.6662,
                                   0.647, 0.6293, 0.6115, 0.5924, 0.5727, 0.5535, 0.5329, 0.5123, 0.492, 0.4718, 0.4503,
                                   0.4292, 0.4087, 0.39, 0.3728, 0.3555, 0.3378, 0.3201, 0.3026, 0.2861, 0.2699, 0.2539,
                                   0.238, 0.222, 0.2065, 0.1929, 0.1797, 0.1669, 0.1548, 0.1434, 0.1326, 0.1224, 0.1127,
                                   0.1035, 0.0958, 0.0885, 0.0821, 0.0766, 0.0716, 0.0668, 0.0621, 0.0575, 0.0531,
                                   0.0486, 0.0442, 0.04, 0.0357, 0.032, 0.0284, 0.0252, 0.0229, 0.021, 0.0193, 0.0177,
                                   0.0161, 0.0145, 0.0129, 0.0113, 0.0097, 0.0082, 0.0068, 0.0057, 0.0049, 0.0043,
                                   0.0038, 0.0034, 0.0031, 0.0027, 0.0024, 0.0021, 0.0018, 0.0016, 0.0015, 0.0014,
                                   0.0013, 0.0011, 0.001, 0.0009, 0.0008, 0.0007, 0.0006, 0.0005, 0.0003, 0.0002, 0.0001]
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
        self.assertAlmostEqual(resp2['resilience_hours_min'], resp1['resilience_hours_min'], places=1)
        self.assertAlmostEqual(1, resp2['resilience_hours_avg'] / resp1['resilience_hours_avg'], places=1)

        for x, y in zip(resp1['probs_of_surviving'], resp2['probs_of_surviving']):
            self.assertAlmostEquals(x, y, places=1)

    def test_grouped_probs_of_surviving(self):
        inputs = self.inputs
        inputs.update(diesel_kw=0, fuel_available=0, m=0, b=0)

        # Output parse from existing simulation
        expected = {
            "probs_of_surviving_by_month": [
                    [1, 0.7688, 0.7003, 0.6277, 0.5511, 0.4785, 0.4005, 0.3266, 0.2769, 0.2312, 0.1989, 0.1774, 0.168,
                      0.1586, 0.1519, 0.1452, 0.1358, 0.1263, 0.1169, 0.1075, 0.0981, 0.0887, 0.0793, 0.0672, 0.0591,
                      0.0538, 0.0484, 0.043, 0.0376, 0.0323, 0.0309, 0.0296, 0.0282, 0.0269, 0.0255, 0.0242, 0.0228,
                      0.0215, 0.0202, 0.0188, 0.0175, 0.0161, 0.0148, 0.0134, 0.0121, 0.0108, 0.0094, 0.0081, 0.0067,
                      0.0054, 0.004, 0.0027, 0.0013],
                    [1, 0.7796, 0.7124, 0.6465, 0.5685, 0.4946, 0.4207, 0.3441, 0.2957, 0.2487, 0.2137, 0.1989,
                       0.1855, 0.1747, 0.168, 0.1613, 0.1505, 0.1398, 0.129, 0.1183, 0.1075, 0.0968, 0.086, 0.0753,
                       0.0659, 0.0591, 0.0524, 0.0457, 0.039, 0.0336, 0.0309, 0.0296, 0.0282, 0.0269, 0.0255, 0.0242,
                       0.0228, 0.0215, 0.0202, 0.0188, 0.0175, 0.0161, 0.0148, 0.0134, 0.0121, 0.0108, 0.0094, 0.0081,
                       0.0067, 0.0054, 0.004, 0.0027, 0.0013]
            ],
            "probs_of_surviving_by_hour_of_the_day": [
                [1, 1, 1, 0.9863, 0.8986, 0.8, 0.5233, 0.2247, 0.1671, 0.1644, 0.1644, 0.1644, 0.1644, 0.1644,
                      0.1616, 0.1616, 0.1616, 0.1534, 0.1425, 0.1068, 0.1068, 0.1068, 0.1068, 0.1068, 0.1068, 0.1068,
                      0.1068, 0.1068, 0.1068, 0.1068, 0.0795, 0.0438, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082,
                      0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082,
                      0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0027],
                [1, 1, 1, 0.9863, 0.8932, 0.8, 0.6685, 0.411, 0.1836, 0.1507, 0.1479, 0.1479, 0.1479, 0.1479,
                       0.1479, 0.1479, 0.1479, 0.1479, 0.1397, 0.1315, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014,
                       0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.074, 0.0411, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                       0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                       0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0027]
            ]
        }
        resp = simulate_outage(**inputs)

        for e, r in zip([0, 1], [0, 11]):
            for x, y in zip(expected['probs_of_surviving_by_month'][e], resp['probs_of_surviving_by_month'][r]):
                self.assertAlmostEquals(x, y, places=3)

        for e, r in zip([0, 1], [0, 23]):
            for x, y in zip(expected['probs_of_surviving_by_hour_of_the_day'][e],
                            resp['probs_of_surviving_by_hour_of_the_day'][r]):
                self.assertAlmostEquals(x, y, places=3)

    def test_resil_endpoint(self):
        post = json.load(open(os.path.join(self.test_path, 'POST_nested.json'), 'r'))
        r = self.api_client.post(self.submit_url, format='json', data=post)
        reopt_resp = json.loads(r.content)
        uuid = reopt_resp['run_uuid']

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

    def test_financial_resil_check_endpoint(self):
        post = json.load(open(os.path.join(self.test_path, 'POST_nested.json'), 'r'))
        r = self.api_client.post(self.submit_url, format='json', data=post)
        reopt_resp = json.loads(r.content)
        uuid = reopt_resp['run_uuid']

        sites = {
            "resilience_site": {
                "Generator": {
                    "size_kw": 100
                },
                "Storage": {
                    "size_kw": 100,
                    "size_kwh": 100
                },
                "PV": {
                    "size_kw": 100
                },
                "Wind": {
                    "size_kw": 100
                }
            },
            "financial_site": {
                "Generator": {
                    "size_kw": 100
                },
                "Storage": {
                    "size_kw": 100,
                    "size_kwh": 100
                },
                "PV": {
                    "size_kw": 100
                },
                "Wind": {
                    "size_kw": 100
                }
            }
        }
        resp = self.api_client.post(self.results_url.replace('<run_uuid>', uuid) + "financial_outage_sim/",
                                    format='json', data=sites)
        self.assertEqual(resp.status_code, 200)

    def test_financial_resil_check(self):
        # same input but different type (float and int)
        resilience_run_site_result = {"pv_size_kw": 100,
                                      "storage_size_kw": 100,
                                      "storage_size_kwh": 300,
                                      "gen_size_kw": 20,
                                      "wind_size_kw": 0}
        financial_run_site_result = {"pv_size_kw": 100.0,
                                     "storage_size_kw": 100.0,
                                     "storage_size_kwh": 300.0,
                                     "gen_size_kw": 20.0,
                                     "wind_size_kw": 0.0
                                     }
        resp = simulate_outage(financial_outage_sim="financial_outage_sim",
                               resilience_run_site_result=resilience_run_site_result,
                               financial_run_site_result=financial_run_site_result)
        self.assertTrue(resp)

        # different input
        resilience_run_site_result = {"pv_size_kw": 100,
                                      "storage_size_kw": 100,
                                      "storage_size_kwh": 300,
                                      "gen_size_kw": 20,
                                      "wind_size_kw": 0}
        financial_run_site_result = {"pv_size_kw": 50.0,
                                     "storage_size_kw": 100.0,
                                     "storage_size_kwh": 300.0,
                                     "gen_size_kw": 20.0,
                                     "wind_size_kw": 0.0
                                     }
        resp = simulate_outage(financial_outage_sim="financial_outage_sim",
                               resilience_run_site_result=resilience_run_site_result,
                               financial_run_site_result=financial_run_site_result)
        self.assertFalse(resp)

        # different input fields
        resilience_run_site_result = {"pv_size_kw": 100,
                                      "storage_size_kw": 100,
                                      "storage_size_kwh": 300,
                                      "gen_size_kw": 20,
                                      "wind_size_kw": 0}
        financial_run_site_result = {"pv_size_kw": 50.0,
                                     "storage_size_kw": 100.0,
                                     "storage_size_kwh": 300.0,
                                     }
        resp = simulate_outage(financial_outage_sim="financial_outage_sim",
                               resilience_run_site_result=resilience_run_site_result,
                               financial_run_site_result=financial_run_site_result)
        self.assertFalse(resp)

        # different input fields
        resilience_run_site_result = {"pv_size_kw": 100,
                                      "storage_size_kw": 100,
                                      "storage_size_kwh": 300
                                      }
        financial_run_site_result = {"pv_size_kw": 50.0,
                                     "storage_size_kw": 100.0,
                                     "storage_size_kwh": 300.0,
                                     "gen_size_kw": 20,
                                     "wind_size_kw": 0
                                     }
        resp = simulate_outage(financial_outage_sim="financial_outage_sim",
                               resilience_run_site_result=resilience_run_site_result,
                               financial_run_site_result=financial_run_site_result)
        self.assertFalse(resp)