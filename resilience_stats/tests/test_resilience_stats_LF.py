import json
import os
import uuid
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from resilience_stats.outage_simulator_LF import simulate_outage


class TestResilStats(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestResilStats, self).setUp()


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
            "probs_of_surviving": [0.8486,
                                   0.7963,
                                   0.7373,
                                   0.6624,
                                   0.59,
                                   0.5194,
                                   0.4533,
                                   0.4007,
                                   0.3583,
                                   0.3231,
                                   0.2934,
                                   0.2692,
                                   0.2473,
                                   0.2298,
                                   0.2152,
                                   0.2017,
                                   0.1901,
                                   0.1795,
                                   0.1703,
                                   0.1618,
                                   0.1539,
                                   0.1465,
                                   0.139,
                                   0.1322,
                                   0.126,
                                   0.1195,
                                   0.1134,
                                   0.1076,
                                   0.1024,
                                   0.0979,
                                   0.0938,
                                   0.0898,
                                   0.0858,
                                   0.0818,
                                   0.0779,
                                   0.0739,
                                   0.0699,
                                   0.066,
                                   0.0619,
                                   0.0572,
                                   0.0524,
                                   0.0477,
                                   0.0429,
                                   0.038,
                                   0.0331,
                                   0.0282,
                                   0.0233,
                                   0.0184,
                                   0.015,
                                   0.012,
                                   0.0099,
                                   0.0083,
                                   0.0073,
                                   0.0068,
                                   0.0064,
                                   0.0062,
                                   0.0059,
                                   0.0057,
                                   0.0055,
                                   0.0053,
                                   0.005,
                                   0.0048,
                                   0.0046,
                                   0.0043,
                                   0.0041,
                                   0.0037,
                                   0.0032,
                                   0.0027,
                                   0.0023,
                                   0.0018,
                                   0.0014,
                                   0.0009,
                                   0.0007,
                                   0.0006,
                                   0.0005,
                                   0.0003,
                                   0.0002,
                                   0.0001],
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
            'resilience_hours_min': 24,
            'resilience_hours_max': 131,
            'resilience_hours_avg': 57.86,
            "outage_durations": range(1, 132),
            "probs_of_surviving":[
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   1.0,
                                   0.9999,
                                   0.9981,
                                   0.9954,
                                   0.9933,
                                   0.9893,
                                   0.986,
                                   0.9826,
                                   0.9774,
                                   0.9711,
                                   0.9634,
                                   0.9539,
                                   0.9432,
                                   0.9293,
                                   0.9121,
                                   0.8929,
                                   0.8733,
                                   0.8531,
                                   0.8316,
                                   0.8087,
                                   0.785,
                                   0.7587,
                                   0.7309,
                                   0.7005,
                                   0.674,
                                   0.6481,
                                   0.6218,
                                   0.5974,
                                   0.5751,
                                   0.5533,
                                   0.5323,
                                   0.5103,
                                   0.4876,
                                   0.4651,
                                   0.4432,
                                   0.4216,
                                   0.4007,
                                   0.3804,
                                   0.3604,
                                   0.3401,
                                   0.3212,
                                   0.3025,
                                   0.2839,
                                   0.2671,
                                   0.2524,
                                   0.2388,
                                   0.2261,
                                   0.2154,
                                   0.2058,
                                   0.1961,
                                   0.1865,
                                   0.1775,
                                   0.1685,
                                   0.1592,
                                   0.1497,
                                   0.1398,
                                   0.13,
                                   0.1204,
                                   0.1108,
                                   0.1019,
                                   0.0938,
                                   0.0866,
                                   0.0803,
                                   0.0745,
                                   0.0695,
                                   0.0652,
                                   0.0611,
                                   0.057,
                                   0.0529,
                                   0.0489,
                                   0.0449,
                                   0.0409,
                                   0.037,
                                   0.0332,
                                   0.0296,
                                   0.0259,
                                   0.0223,
                                   0.0189,
                                   0.0158,
                                   0.013,
                                   0.0108,
                                   0.009,
                                   0.0075,
                                   0.0067,
                                   0.0062,
                                   0.0057,
                                   0.0054,
                                   0.005,
                                   0.0047,
                                   0.0043,
                                   0.004,
                                   0.0037,
                                   0.0033,
                                   0.003,
                                   0.0026,
                                   0.0023,
                                   0.0019,
                                   0.0017,
                                   0.0015,
                                   0.0013,
                                   0.001,
                                   0.0008,
                                   0.0007,
                                   0.0006,
                                   0.0005,
                                   0.0003,
                                   0.0002,
                                   0.0001
                                ]
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
        
    def test_flexible_timesteps(self):
        """
        Same input with different timesteps-per-hour should have almost equal results.
        """
        resp1 = simulate_outage(**self.inputs1)
        resp2 = simulate_outage(**self.inputs2)

        self.assertAlmostEqual(1, resp2['resilience_hours_max']/resp1['resilience_hours_max'], places=1)
        self.assertAlmostEqual(1, resp2['resilience_hours_min'] / resp1['resilience_hours_min'], places=1)
        self.assertAlmostEqual(1, resp2['resilience_hours_avg'] / resp1['resilience_hours_avg'], places=1)

        for x, y in zip(resp1['probs_of_surviving'], resp2['probs_of_surviving']):
            self.assertAlmostEquals(x, y, places=1)
