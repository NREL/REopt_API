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
        Use self.inputs to test the outage simulator for expected outputs.
        :return: None
        """
        inputs = self.inputs
        inputs['diesel_kw'] = 0
        inputs['fuel_available'] = 0
        inputs['m'] = 0
        inputs['b'] = 0

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
        Use self.inputs to test the outage simulator for expected outputs.
        :return: None
        """
        expected = {
            'resilience_hours_min': 27,
            'resilience_hours_max': 143,
            'resilience_hours_avg': 67.9,
            "outage_durations": range(1, 144),
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
                1.0,
                1.0,
                1.0,
                0.9999,
                0.999,
                0.9982,
                0.9962,
                0.9942,
                0.9926,
                0.9911,
                0.9893,
                0.9865,
                0.9822,
                0.9772,
                0.9697,
                0.9626,
                0.9538,
                0.9445,
                0.9347,
                0.9242,
                0.9126,
                0.8998,
                0.8854,
                0.8676,
                0.8485,
                0.8301,
                0.807,
                0.7837,
                0.7629,
                0.743,
                0.7234,
                0.7042,
                0.6862,
                0.6697,
                0.6533,
                0.6361,
                0.62,
                0.6009,
                0.5811,
                0.5607,
                0.5405,
                0.5195,
                0.4985,
                0.4779,
                0.4582,
                0.438,
                0.4172,
                0.3973,
                0.378,
                0.3605,
                0.3443,
                0.3277,
                0.3119,
                0.2961,
                0.2803,
                0.265,
                0.2499,
                0.2358,
                0.2213,
                0.2062,
                0.1916,
                0.1788,
                0.1668,
                0.1545,
                0.1429,
                0.1315,
                0.1208,
                0.111,
                0.1013,
                0.0924,
                0.0847,
                0.0779,
                0.0718,
                0.0668,
                0.0622,
                0.0579,
                0.0534,
                0.049,
                0.0444,
                0.04,
                0.0357,
                0.0315,
                0.0276,
                0.0241,
                0.021,
                0.0187,
                0.0169,
                0.0154,
                0.014,
                0.0128,
                0.0115,
                0.0103,
                0.009,
                0.0078,
                0.0065,
                0.0056,
                0.0048,
                0.0042,
                0.0038,
                0.0034,
                0.0031,
                0.0027,
                0.0024,
                0.0022,
                0.0019,
                0.0017,
                0.0015,
                0.0014,
                0.0013,
                0.0011,
                0.001,
                0.0009,
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

    def test_no_resilience(self):
        self.inputs.update(pv_kw_ac_hourly=[], batt_kw=0, diesel_kw=0)

        resp = simulate_outage(**self.inputs)

        self.assertEqual(0, resp['resilience_hours_min'])
        self.assertEqual(0, resp['resilience_hours_max'])
        self.assertEqual(0, resp['resilience_hours_avg'])
        self.assertEqual(None, resp['outage_durations'])
        self.assertEqual(None, resp['probs_of_surviving'])
        
    def test_flexible_timesteps(self):
        """
        Use self.inputs to flexible timesteps
        :return: None
        """
        resp1 = simulate_outage(**self.inputs1)
        resp2 = simulate_outage(**self.inputs2)
        
        prob2 = [sum(resp2['probs_of_surviving'][i:i+2])/2.0 for i in range(0,8760*2,2)]

        self.assertAlmostEqual(resp1['resilience_hours_max'], resp2['resilience_hours_max'], places=0)
        self.assertAlmostEqual(resp1['resilience_hours_avg'], resp2['resilience_hours_avg'], places=-1)
        
        # self.assertAlmostEqual(resp1['resilience_hours_min'], resp2['resilience_hours_min'], places=0)
        # self.assertAlmostEqual(resp1['outage_durations'], resp2['outage_durations'], places=3)
        # for x, y in zip(resp1['probs_of_surviving'], prob2):
        #     self.assertAlmostEquals(x, y, places=1)
