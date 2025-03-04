# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
import json
import os
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from resilience_stats.outage_simulator_LF import simulate_outages


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

        self.inputs = readFiles('')
        self.inputs1 = readFiles('timestep_1')
        self.inputs2 = readFiles('timestep_2')

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
            'resilience_hours_avg': 10.23,
            "outage_durations": list(range(1, 79)),
            "probs_of_surviving": [0.8486, 0.7963, 0.7373, 0.6624, 0.59, 0.5194, 0.4533, 0.4007, 0.3583, 0.3231, 0.2933,
                                0.2691, 0.2471, 0.2297, 0.215, 0.2015, 0.1897, 0.1788, 0.1694, 0.1608, 0.153, 0.1454,
                                0.1381, 0.1308, 0.1247, 0.1184, 0.1122, 0.1065, 0.1013, 0.0968, 0.0927, 0.0887, 0.0847,
                                0.0807, 0.0767, 0.0727, 0.0687, 0.0648, 0.0607, 0.0562, 0.0516, 0.047, 0.0425, 0.0376,
                                0.0326, 0.0277, 0.0228, 0.0179, 0.0146, 0.0116, 0.0097, 0.0081, 0.0071, 0.0066, 0.0062,
                                0.0059, 0.0057, 0.0055, 0.0053, 0.005, 0.0048, 0.0046, 0.0043, 0.0041, 0.0039, 0.0037,
                                0.0032, 0.0027, 0.0023, 0.0018, 0.0014, 0.0009, 0.0007, 0.0006, 0.0005, 0.0003, 0.0002,
                                0.0001],
            "probs_of_surviving_by_month": [
                [1.0, 0.7688, 0.7003, 0.6277, 0.5511, 0.4785, 0.4005, 0.3266, 0.2769, 0.2312, 0.1989, 0.1774, 0.168,
                 0.1586, 0.1519, 0.1452, 0.1358, 0.1263, 0.1169, 0.1075, 0.0981, 0.0887, 0.078, 0.0672, 0.0591, 0.0538,
                 0.0484, 0.043, 0.0376, 0.0323, 0.0309, 0.0296, 0.0282, 0.0269, 0.0255, 0.0242, 0.0228, 0.0215, 0.0202,
                 0.0188, 0.0175, 0.0161, 0.0148, 0.0134, 0.0121, 0.0108, 0.0094, 0.0081, 0.0067, 0.0054, 0.004, 0.0027,
                 0.0013, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.8036, 0.7381, 0.6756, 0.6131, 0.5208, 0.4315, 0.3571, 0.3021, 0.2589, 0.2262, 0.2024, 0.1935,
                 0.183, 0.1756, 0.1696, 0.1607, 0.1548, 0.1473, 0.1384, 0.1324, 0.1265, 0.1205, 0.1146, 0.1086, 0.1027,
                 0.0967, 0.0908, 0.0848, 0.0804, 0.0774, 0.0744, 0.0729, 0.0714, 0.0699, 0.0685, 0.067, 0.0655, 0.064,
                 0.061, 0.0565, 0.0521, 0.0476, 0.0446, 0.0387, 0.0327, 0.0268, 0.0208, 0.0149, 0.0134, 0.0119, 0.0104,
                 0.0089, 0.0089, 0.0089, 0.0089, 0.0089, 0.0089, 0.0089, 0.0089, 0.0089, 0.0089, 0.0089, 0.0089, 0.0089,
                 0.0089, 0.0089, 0.0074, 0.006, 0.0045, 0.003, 0.0015, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.8212, 0.7527, 0.6935, 0.6035, 0.5376, 0.461, 0.3898, 0.328, 0.2782, 0.2419, 0.2124, 0.1922,
                 0.1761, 0.1667, 0.1559, 0.1452, 0.1358, 0.129, 0.1223, 0.1169, 0.1116, 0.1062, 0.1008, 0.0954, 0.0901,
                 0.0847, 0.0793, 0.0766, 0.0753, 0.0739, 0.0726, 0.0712, 0.0699, 0.0685, 0.0672, 0.0659, 0.0645, 0.0632,
                 0.0618, 0.0578, 0.0538, 0.0484, 0.043, 0.0376, 0.0323, 0.0269, 0.0215, 0.0161, 0.0134, 0.0108, 0.0081,
                 0.0054, 0.0027, 0.0013, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.8889, 0.8292, 0.7694, 0.6917, 0.6194, 0.5542, 0.4903, 0.4431, 0.4069, 0.3708, 0.3375, 0.3069,
                 0.2792, 0.2639, 0.25, 0.2389, 0.2278, 0.2181, 0.2083, 0.1986, 0.1903, 0.1833, 0.1764, 0.1694, 0.1625,
                 0.1556, 0.1486, 0.1417, 0.1347, 0.1278, 0.1208, 0.1139, 0.1069, 0.1, 0.0931, 0.0861, 0.0792, 0.0722,
                 0.0653, 0.0583, 0.0514, 0.0444, 0.0375, 0.0306, 0.0236, 0.0167, 0.0097, 0.0028, 0.0014, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.9059, 0.8723, 0.8293, 0.7796, 0.6962, 0.6358, 0.578, 0.5215, 0.4785, 0.4409, 0.4005, 0.3656,
                 0.3333, 0.3051, 0.2809, 0.2608, 0.2419, 0.2285, 0.2177, 0.207, 0.1989, 0.1935, 0.1882, 0.1828, 0.1774,
                 0.172, 0.1667, 0.1613, 0.1559, 0.1505, 0.1452, 0.1398, 0.1344, 0.129, 0.1237, 0.1183, 0.1129, 0.1075,
                 0.1022, 0.0968, 0.0914, 0.086, 0.0806, 0.0753, 0.0699, 0.0645, 0.0591, 0.0538, 0.0484, 0.043, 0.039,
                 0.0363, 0.0349, 0.0336, 0.0323, 0.0309, 0.0296, 0.0282, 0.0269, 0.0255, 0.0242, 0.0228, 0.0215, 0.0202,
                 0.0188, 0.0175, 0.0161, 0.0148, 0.0134, 0.0121, 0.0108, 0.0094, 0.0081, 0.0067, 0.0054, 0.004, 0.0027,
                 0.0013],
                [1.0, 0.9111, 0.8792, 0.8292, 0.7597, 0.6708, 0.5944, 0.5403, 0.4875, 0.4444, 0.4028, 0.3667, 0.3306,
                 0.2972, 0.2667, 0.2431, 0.225, 0.2083, 0.1944, 0.1861, 0.1792, 0.1736, 0.1681, 0.1625, 0.1569, 0.1514,
                 0.1458, 0.1403, 0.1347, 0.1292, 0.1236, 0.1181, 0.1125, 0.1069, 0.1014, 0.0958, 0.0903, 0.0847, 0.0792,
                 0.0736, 0.0681, 0.0625, 0.0569, 0.0514, 0.0458, 0.0403, 0.0347, 0.0292, 0.0236, 0.0181, 0.0125, 0.0083,
                 0.0042, 0.0028, 0.0014, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.9194, 0.8831, 0.8293, 0.7433, 0.6815, 0.6022, 0.5497, 0.5067, 0.4718, 0.4368, 0.4046, 0.3696,
                 0.3414, 0.3172, 0.2997, 0.2823, 0.2661, 0.2513, 0.2392, 0.2285, 0.2177, 0.207, 0.1976, 0.1895, 0.1815,
                 0.1734, 0.1653, 0.1573, 0.1492, 0.1425, 0.1358, 0.129, 0.1223, 0.1156, 0.1089, 0.1022, 0.0954, 0.0887,
                 0.082, 0.0753, 0.0685, 0.0618, 0.0551, 0.0484, 0.0417, 0.0349, 0.0282, 0.0215, 0.0148, 0.0081, 0.0054,
                 0.0027, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.8992, 0.8589, 0.8065, 0.7285, 0.664, 0.5968, 0.5228, 0.4583, 0.4086, 0.3723, 0.336, 0.3024,
                 0.2702, 0.2433, 0.2177, 0.2016, 0.1909, 0.1815, 0.1734, 0.1653, 0.1586, 0.1519, 0.1465, 0.1411, 0.1358,
                 0.129, 0.1237, 0.1183, 0.1129, 0.1075, 0.1022, 0.0968, 0.0914, 0.086, 0.0806, 0.0753, 0.0699, 0.0645,
                 0.0591, 0.0538, 0.0484, 0.043, 0.0376, 0.0323, 0.0269, 0.0215, 0.0161, 0.0108, 0.0054, 0.0027, 0.0013,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.8708, 0.8347, 0.7819, 0.7042, 0.6181, 0.5486, 0.475, 0.4333, 0.4028, 0.3708, 0.3375, 0.3083,
                 0.2819, 0.2611, 0.2472, 0.2361, 0.2278, 0.2194, 0.2139, 0.2083, 0.2028, 0.1972, 0.1917, 0.1861, 0.1806,
                 0.175, 0.1694, 0.1639, 0.1583, 0.1528, 0.1472, 0.1417, 0.1361, 0.1306, 0.125, 0.1194, 0.1139, 0.1083,
                 0.1028, 0.0972, 0.0917, 0.0861, 0.0792, 0.0722, 0.0653, 0.0583, 0.0514, 0.0444, 0.0389, 0.0333, 0.0306,
                 0.0292, 0.0278, 0.0264, 0.025, 0.0236, 0.0222, 0.0208, 0.0194, 0.0181, 0.0167, 0.0153, 0.0139, 0.0125,
                 0.0111, 0.0097, 0.0083, 0.0069, 0.0056, 0.0042, 0.0028, 0.0014, 0, 0, 0, 0, 0, 0],
                [1.0, 0.8199, 0.7608, 0.7016, 0.6223, 0.5685, 0.5161, 0.4543, 0.3952, 0.3495, 0.3172, 0.2863, 0.2648,
                 0.246, 0.2272, 0.211, 0.1976, 0.1868, 0.1747, 0.1653, 0.1559, 0.1478, 0.1411, 0.1344, 0.1277, 0.121,
                 0.1142, 0.1075, 0.1035, 0.0995, 0.0954, 0.0914, 0.0874, 0.0833, 0.0793, 0.0753, 0.0712, 0.0672, 0.0645,
                 0.0605, 0.0551, 0.0497, 0.0444, 0.039, 0.0336, 0.0282, 0.0228, 0.0175, 0.0121, 0.0108, 0.0094, 0.0081,
                 0.0081, 0.0081, 0.0081, 0.0081, 0.0081, 0.0081, 0.0081, 0.0081, 0.0081, 0.0081, 0.0081, 0.0081, 0.0081,
                 0.0081, 0.0081, 0.0067, 0.0054, 0.004, 0.0027, 0.0013, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.7931, 0.7319, 0.6542, 0.5819, 0.525, 0.4653, 0.4056, 0.3542, 0.3153, 0.2792, 0.2542, 0.2375,
                 0.2208, 0.2069, 0.1958, 0.1819, 0.1694, 0.1542, 0.1417, 0.1319, 0.1222, 0.1125, 0.1028, 0.0875, 0.0806,
                 0.0736, 0.0667, 0.0597, 0.0542, 0.0486, 0.0458, 0.0431, 0.0403, 0.0375, 0.0347, 0.0319, 0.0292, 0.0264,
                 0.0236, 0.0208, 0.0181, 0.0167, 0.0153, 0.0125, 0.0097, 0.0069, 0.0042, 0.0014, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.7796, 0.7124, 0.6465, 0.5685, 0.4946, 0.4207, 0.3441, 0.2957, 0.2487, 0.2137, 0.1989, 0.1855,
                 0.1747, 0.168, 0.1613, 0.1505, 0.1398, 0.129, 0.1183, 0.1075, 0.0968, 0.086, 0.0753, 0.0659, 0.0591,
                 0.0524, 0.0457, 0.039, 0.0336, 0.0309, 0.0296, 0.0282, 0.0269, 0.0255, 0.0242, 0.0228, 0.0215, 0.0202,
                 0.0188, 0.0175, 0.0161, 0.0148, 0.0134, 0.0121, 0.0108, 0.0094, 0.0081, 0.0067, 0.0054, 0.004, 0.0027,
                 0.0013, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
            "probs_of_surviving_by_hour_of_the_day": [
                [1.0, 1.0, 1.0, 0.9863, 0.8986, 0.8, 0.5233, 0.2247, 0.1671, 0.1644, 0.1644, 0.1644, 0.1644, 0.1644,
                 0.1616, 0.1616, 0.1616, 0.1534, 0.1425, 0.1068, 0.1068, 0.1068, 0.1068, 0.1068, 0.1068, 0.1068, 0.1068,
                 0.1068, 0.1068, 0.1068, 0.0795, 0.0438, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082,
                 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082,
                 0.0082, 0.0082, 0.0027, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 1.0, 1.0, 0.9863, 0.8959, 0.6301, 0.3014, 0.2164, 0.2137, 0.2137, 0.2137, 0.211, 0.211, 0.2082,
                 0.2082, 0.2082, 0.1973, 0.1863, 0.126, 0.126, 0.126, 0.126, 0.126, 0.126, 0.126, 0.126, 0.126, 0.126,
                 0.126, 0.0959, 0.0521, 0.0164, 0.0164, 0.0164, 0.0164, 0.0164, 0.0164, 0.0164, 0.0164, 0.0164, 0.0164,
                 0.0164, 0.0164, 0.0164, 0.0164, 0.0164, 0.0164, 0.0164, 0.0164, 0.0164, 0.0164, 0.0164, 0.0164, 0.0137,
                 0.0082, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027,
                 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027],
                [1.0, 1.0, 1.0, 0.9863, 0.7123, 0.3644, 0.2904, 0.2822, 0.2822, 0.2822, 0.2822, 0.2795, 0.274, 0.274,
                 0.274, 0.2603, 0.2356, 0.1452, 0.1452, 0.1452, 0.1452, 0.1452, 0.1452, 0.1452, 0.1452, 0.1452, 0.1452,
                 0.1452, 0.1151, 0.0575, 0.0219, 0.0219, 0.0219, 0.0219, 0.0219, 0.0219, 0.0219, 0.0219, 0.0219, 0.0219,
                 0.0219, 0.0219, 0.0219, 0.0219, 0.0219, 0.0219, 0.0219, 0.0219, 0.0219, 0.0219, 0.0219, 0.0219, 0.0192,
                 0.0082, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027,
                 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0],
                [1.0, 1.0, 1.0, 0.8055, 0.474, 0.3616, 0.3562, 0.3562, 0.3562, 0.3562, 0.3534, 0.3479, 0.3479, 0.3479,
                 0.3233, 0.2904, 0.1836, 0.1836, 0.1836, 0.1836, 0.1836, 0.1836, 0.1836, 0.1836, 0.1808, 0.1808, 0.1808,
                 0.1397, 0.0712, 0.0329, 0.0329, 0.0329, 0.0329, 0.0329, 0.0329, 0.0329, 0.0329, 0.0329, 0.0329, 0.0329,
                 0.0329, 0.0329, 0.0329, 0.0329, 0.0329, 0.0329, 0.0329, 0.0329, 0.0329, 0.0329, 0.0329, 0.0274, 0.0137,
                 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027,
                 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0, 0],
                [1.0, 1.0, 0.863, 0.5315, 0.4521, 0.4493, 0.4466, 0.4466, 0.4466, 0.4438, 0.4384, 0.4384, 0.4356, 0.411,
                 0.3616, 0.2055, 0.2055, 0.2055, 0.2055, 0.2055, 0.2055, 0.2055, 0.2055, 0.2055, 0.2027, 0.2027, 0.1589,
                 0.0904, 0.0521, 0.0521, 0.0521, 0.0521, 0.0521, 0.0521, 0.0521, 0.0521, 0.0521, 0.0521, 0.0521, 0.0521,
                 0.0521, 0.0521, 0.0521, 0.0521, 0.0521, 0.0521, 0.0521, 0.0521, 0.0521, 0.0521, 0.0411, 0.0247, 0.0027,
                 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027,
                 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0, 0, 0],
                [1.0, 0.8712, 0.5808, 0.5014, 0.4959, 0.4959, 0.4959, 0.4959, 0.4932, 0.4877, 0.4877, 0.4849, 0.4575,
                 0.4027, 0.2137, 0.2137, 0.2137, 0.2137, 0.2137, 0.2137, 0.2137, 0.2137, 0.2137, 0.2137, 0.211, 0.1699,
                 0.1014, 0.063, 0.063, 0.063, 0.063, 0.063, 0.063, 0.063, 0.063, 0.063, 0.063, 0.063, 0.063, 0.063,
                 0.063, 0.063, 0.063, 0.063, 0.063, 0.063, 0.063, 0.063, 0.063, 0.0521, 0.0274, 0.0027, 0.0027, 0.0027,
                 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027,
                 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0.0027, 0, 0, 0, 0],
                [1.0, 0.7041, 0.6685, 0.6685, 0.6658, 0.6658, 0.6658, 0.663, 0.6575, 0.6575, 0.6548, 0.6055, 0.526,
                 0.2712, 0.2712, 0.2685, 0.2685, 0.2685, 0.2685, 0.2685, 0.2685, 0.2685, 0.2685, 0.2658, 0.2219, 0.1534,
                 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151,
                 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.0767, 0.0438, 0.0082, 0.0082,
                 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082,
                 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0055, 0.0027, 0, 0, 0, 0, 0],
                [1.0, 0.937, 0.9233, 0.9178, 0.9068, 0.9068, 0.9014, 0.8904, 0.8904, 0.8767, 0.7205, 0.5836, 0.3014,
                 0.3014, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2521, 0.1671, 0.1288,
                 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288,
                 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.0904, 0.0466, 0.011, 0.011, 0.011,
                 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011,
                 0.011, 0.011, 0.011, 0.011, 0.011, 0.0082, 0.0027, 0, 0, 0, 0, 0, 0],
                [1.0, 0.9671, 0.9562, 0.9479, 0.9479, 0.9425, 0.9288, 0.926, 0.9096, 0.7397, 0.5918, 0.3014, 0.3014,
                 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2521, 0.1671, 0.1288, 0.1288,
                 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288,
                 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.0904, 0.0466, 0.011, 0.011, 0.011, 0.011,
                 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011,
                 0.011, 0.011, 0.011, 0.011, 0.0082, 0.0027, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.9699, 0.9589, 0.9589, 0.9534, 0.937, 0.937, 0.9178, 0.7397, 0.5973, 0.3014, 0.3014, 0.2986,
                 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2548, 0.1671, 0.1288, 0.1288, 0.1288,
                 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288,
                 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.0904, 0.0466, 0.011, 0.011, 0.011, 0.011, 0.011,
                 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011,
                 0.011, 0.011, 0.011, 0.0082, 0.0027, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.9781, 0.9699, 0.9644, 0.9479, 0.9452, 0.9288, 0.7397, 0.5973, 0.3014, 0.3014, 0.2986, 0.2986,
                 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2548, 0.1671, 0.1288, 0.1288, 0.1288, 0.1288,
                 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288,
                 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.0904, 0.0466, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011,
                 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011,
                 0.011, 0.011, 0.0082, 0.0027, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.9863, 0.9726, 0.9534, 0.9507, 0.9315, 0.7397, 0.5973, 0.3014, 0.3014, 0.2986, 0.2986, 0.2986,
                 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2548, 0.1671, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288,
                 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1288,
                 0.1288, 0.1288, 0.1288, 0.1288, 0.0904, 0.0466, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011,
                 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011, 0.011,
                 0.0082, 0.0027, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.9836, 0.9616, 0.9589, 0.937, 0.7397, 0.5973, 0.3014, 0.3014, 0.2986, 0.2986, 0.2986, 0.2986,
                 0.2986, 0.2986, 0.2986, 0.2986, 0.2986, 0.2466, 0.1534, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151,
                 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151,
                 0.1151, 0.1151, 0.1151, 0.0795, 0.0438, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082,
                 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082, 0.0082,
                 0.0082, 0.0082, 0.0027, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.9644, 0.9616, 0.9397, 0.7397, 0.5973, 0.3014, 0.3014, 0.2986, 0.2986, 0.2986, 0.2986, 0.2986,
                 0.2986, 0.2986, 0.2959, 0.2932, 0.2438, 0.1507, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123,
                 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123,
                 0.1123, 0.1123, 0.0795, 0.0411, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0027, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.9726, 0.9479, 0.7397, 0.5973, 0.3014, 0.3014, 0.2986, 0.2986, 0.2986, 0.2986, 0.2959, 0.2932,
                 0.2932, 0.2904, 0.2904, 0.2384, 0.1534, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151,
                 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151, 0.1151,
                 0.1151, 0.0822, 0.0411, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0027, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.9562, 0.7452, 0.6027, 0.3014, 0.3014, 0.2986, 0.2986, 0.2932, 0.2932, 0.2932, 0.2904, 0.2904,
                 0.2822, 0.2822, 0.2356, 0.1479, 0.1096, 0.1096, 0.1096, 0.1096, 0.1096, 0.1096, 0.1096, 0.1096, 0.1096,
                 0.1096, 0.1096, 0.1096, 0.1096, 0.1096, 0.1096, 0.1096, 0.1096, 0.1096, 0.1096, 0.1096, 0.1096, 0.1096,
                 0.0822, 0.0411, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0027,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.7479, 0.6, 0.3014, 0.3014, 0.2959, 0.2932, 0.2932, 0.2877, 0.2877, 0.2822, 0.2822, 0.2795,
                 0.2575, 0.2082, 0.1397, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014,
                 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.0767,
                 0.0411, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0027, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.6137, 0.3014, 0.3014, 0.2959, 0.2932, 0.2877, 0.2877, 0.2849, 0.2822, 0.2767, 0.2575, 0.2521,
                 0.2055, 0.1315, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014,
                 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.074, 0.0411,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0027, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.3123, 0.3123, 0.3096, 0.3068, 0.3068, 0.2986, 0.2986, 0.2932, 0.2877, 0.2795, 0.2685, 0.2164,
                 0.126, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014,
                 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.074, 0.0411, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0027, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.326, 0.3123, 0.3123, 0.3096, 0.3068, 0.3014, 0.2986, 0.2904, 0.2795, 0.2685, 0.2164, 0.1205,
                 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014,
                 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.074, 0.0411, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0027, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 0.3123, 0.3123, 0.3123, 0.3096, 0.3068, 0.2986, 0.2877, 0.2822, 0.2712, 0.2164, 0.126, 0.1041,
                 0.1041, 0.1041, 0.1041, 0.1041, 0.1041, 0.1041, 0.1041, 0.1041, 0.1041, 0.1041, 0.1014, 0.1014, 0.1014,
                 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.074, 0.0411, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0027, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0],
                [1.0, 0.7644, 0.7644, 0.7479, 0.6986, 0.6493, 0.5863, 0.4849, 0.4027, 0.2548, 0.1534, 0.1123, 0.1123,
                 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1123, 0.1096, 0.1014, 0.1014, 0.1014, 0.1014,
                 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.074, 0.0411, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0027, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0],
                [1.0, 1.0, 1.0, 0.9753, 0.9068, 0.8301, 0.7178, 0.5616, 0.3452, 0.1753, 0.1315, 0.1288, 0.1288, 0.1288,
                 0.1288, 0.1288, 0.1288, 0.1288, 0.1288, 0.1233, 0.1178, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014,
                 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.074, 0.0411, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0027, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1.0, 1.0, 1.0, 0.9863, 0.8932, 0.8, 0.6685, 0.411, 0.1836, 0.1507, 0.1479, 0.1479, 0.1479, 0.1479,
                 0.1479, 0.1479, 0.1479, 0.1479, 0.1397, 0.1315, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014, 0.1014,
                 0.1014, 0.1014, 0.1014, 0.1014, 0.074, 0.0411, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055, 0.0055,
                 0.0055, 0.0055, 0.0055, 0.0027, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        }
        resp = simulate_outages(**inputs)

        self.assertAlmostEqual(expected['resilience_hours_min'], resp['resilience_hours_min'], places=3)
        self.assertAlmostEqual(expected['resilience_hours_max'], resp['resilience_hours_max'], places=3)
        self.assertAlmostEqual(expected['resilience_hours_avg'], resp['resilience_hours_avg'], places=3)
        self.assertAlmostEqual(expected['outage_durations'], resp['outage_durations'], places=3)
        for x, y in zip(expected['probs_of_surviving'], resp['probs_of_surviving']):
            self.assertAlmostEquals(x, y, places=3)
        for e, r in zip([0, 11], [0, 11]):
            for x, y in zip(expected['probs_of_surviving_by_month'][e], resp['probs_of_surviving_by_month'][r]):
                self.assertAlmostEquals(x, y, places=3)
        for e, r in zip([0, 23], [0, 23]):
            for x, y in zip(expected['probs_of_surviving_by_hour_of_the_day'][e],
                            resp['probs_of_surviving_by_hour_of_the_day'][r]):
                self.assertAlmostEquals(x, y, places=3)

    def test_outage_sim(self):
        """
        With diesel + PV + storage
        """
        expected = {
            'resilience_hours_min': 30,
            'resilience_hours_max': 154,
            'resilience_hours_avg': 82.1,
            "outage_durations": list(range(1, 155)),
            "probs_of_surviving":  [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9999, 0.9998,
                                    0.9997, 0.9985, 0.9973, 0.9965, 0.9951, 0.9937, 0.9921, 0.989, 0.9861, 0.983,
                                    0.9797, 0.976, 0.972, 0.9666, 0.9608, 0.9547, 0.9471, 0.9373, 0.9275, 0.9178,
                                    0.9066, 0.897, 0.8868, 0.8761, 0.8647, 0.8521, 0.8398, 0.8285, 0.816, 0.8035,
                                    0.7928, 0.7809, 0.7693, 0.7561, 0.7436, 0.7301, 0.7159, 0.701, 0.685, 0.6707,
                                    0.6535, 0.6347, 0.6189, 0.6026, 0.5864, 0.5696, 0.5534, 0.5376, 0.5213, 0.5053,
                                    0.4892, 0.4719, 0.4542, 0.4378, 0.4217, 0.4058, 0.3901, 0.3736, 0.3584, 0.3434,
                                    0.3287, 0.3152, 0.3006, 0.2854, 0.2728, 0.2579, 0.2449, 0.2321, 0.2196, 0.2068,
                                    0.1941, 0.1812, 0.1685, 0.1562, 0.1446, 0.1324, 0.1216, 0.1114, 0.1021, 0.0928,
                                    0.084, 0.0752, 0.0675, 0.0603, 0.0533, 0.0466, 0.0411, 0.0371, 0.0333, 0.0296,
                                    0.026, 0.0231, 0.0203, 0.0178, 0.0153, 0.0129, 0.0105, 0.0086, 0.0067, 0.0053,
                                    0.0042, 0.0035, 0.0033, 0.0031, 0.0029, 0.0026, 0.0024, 0.0022, 0.0019, 0.0017,
                                    0.0015, 0.0013, 0.0011, 0.001, 0.0009, 0.0008, 0.0007, 0.0006, 0.0005, 0.0003,
                                    0.0002, 0.0001]
        }
        resp = simulate_outages(**self.inputs)

        self.assertAlmostEqual(expected['resilience_hours_min'], resp['resilience_hours_min'], places=4)
        self.assertAlmostEqual(expected['resilience_hours_max'], resp['resilience_hours_max'], places=4)
        self.assertAlmostEqual(expected['resilience_hours_avg'], resp['resilience_hours_avg'], places=4)
        self.assertListEqual(expected['outage_durations'], resp['outage_durations'])
        for x, y in zip(expected['probs_of_surviving'], resp['probs_of_surviving']):
            self.assertAlmostEquals(x, y, places=4)

    def test_no_resilience(self):
        inputs = self.inputs
        inputs.update(pv_kw_ac_hourly=[], batt_kw=0, diesel_kw=0)
        resp = simulate_outages(**inputs)

        self.assertEqual(0, resp['resilience_hours_min'])
        self.assertEqual(0, resp['resilience_hours_max'])
        self.assertEqual(0, resp['resilience_hours_avg'])
        self.assertEqual([], resp['outage_durations'])
        self.assertEqual([], resp['probs_of_surviving'])
        self.assertEqual([[0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0]], resp['probs_of_surviving_by_month'])
        self.assertEqual([[0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0]], resp['probs_of_surviving_by_hour_of_the_day'])

    def test_flexible_timesteps(self):
        """
        Same input with different timesteps-per-hour should have almost equal results.
        """
        resp1 = simulate_outages(**self.inputs1)
        resp2 = simulate_outages(**self.inputs2)

        self.assertAlmostEqual(1, resp2['resilience_hours_max'] / resp1['resilience_hours_max'], places=1)
        self.assertAlmostEqual(resp2['resilience_hours_min'], resp1['resilience_hours_min'], places=0)
        self.assertAlmostEqual(1, resp2['resilience_hours_avg'] / resp1['resilience_hours_avg'], places=1)

        for x, y in zip(resp1['probs_of_surviving'], resp2['probs_of_surviving']):
            self.assertAlmostEquals(x, y, places=1)

    def test_resil_endpoint(self):
        post = json.load(open(os.path.join('resilience_stats', 'tests', 'POST_nested.json'), 'r'))
        r = self.api_client.post('/v2/job/', format='json', data=post)
        reopt_resp = json.loads(r.content)
        run_uuid = reopt_resp['run_uuid']

        resp = self.api_client.post('/v2/outagesimjob/', format='json', data={"run_uuid": run_uuid, "bau": True})
        self.assertEqual(resp.status_code, 201)
        resp = self.api_client.get('/v2/job/<run_uuid>/resilience_stats/'.replace("<run_uuid>", run_uuid))
        resp_dict = json.loads(resp.content)['outage_sim_results']

        # NOTE: probabilities are sensitive to the SOC series,
        #   which can change while keeping the same optimal LCC
        expected_probs = [0.3902, 0.2338, 0.1919, 0.1532, 0.1178, 0.0844, 0.0538, 0.0305, 0.0131, 0.0066, 0.0033, 0.001]
        for idx, p in enumerate(resp_dict["probs_of_surviving"]):
            self.assertAlmostEqual(p, expected_probs[idx], places=2)
        self.assertEqual(resp_dict["resilience_hours_avg"], 1.28)
        self.assertEqual(resp_dict["outage_durations"], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        self.assertEqual(resp_dict["resilience_hours_min"], 0)
        self.assertEqual(resp_dict["resilience_hours_max"], 12)
        self.assertFalse("resilience_hours_max_bau" in resp_dict)

        """
        financial_check returns true if the financial scenario system capacities are greater than or equal to the
        resilience scenario system capacities
        """
        resp = self.api_client.get(
            '/v2/financial_check/?financial_uuid={0}&resilience_uuid={0}'.format(run_uuid),
            format='json')
        self.assertEqual(resp.status_code, 200)
        results = json.loads(resp.content)
        self.assertTrue(results["survives_specified_outage"])

    def test_outage_sim_chp(self):
        expected = {
            'resilience_hours_min': 0,
            'resilience_hours_max': 10,
            'resilience_hours_avg': 0.01,
            "outage_durations": list(range(1, 11)),
            "probs_of_surviving": [0.0011, 0.001, 0.0009, 0.0008, 0.0007, 0.0006, 0.0005, 0.0003, 0.0002, 0.0001]
        }
        inputs = self.inputs
        inputs.update(pv_kw_ac_hourly=[], batt_kw=0, diesel_kw=0, chp_kw=10, critical_loads_kw=[10]*10 + [11]*8750)
        resp = simulate_outages(**inputs)

        self.assertAlmostEqual(expected['resilience_hours_min'], resp['resilience_hours_min'], places=4)
        self.assertAlmostEqual(expected['resilience_hours_max'], resp['resilience_hours_max'], places=4)
        self.assertAlmostEqual(expected['resilience_hours_avg'], resp['resilience_hours_avg'], places=4)
        self.assertListEqual(expected['outage_durations'], resp['outage_durations'])
        for x, y in zip(expected['probs_of_surviving'], resp['probs_of_surviving']):
            self.assertAlmostEquals(x, y, places=4)
