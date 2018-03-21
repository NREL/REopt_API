from django.test import TestCase
from reo.src.load_profile import BuiltInProfile


class LoadsTestCase(TestCase):

    # mimic user passing in info
    def setUp(self):
        pass

    def test_ashrae_zones(self):

        test_cities = ['Florida City', 'Orlando', 'Tucson', 'Oklahoma City', 'Sacremento', 'San Jose',
                       'Nashville', 'Amarillo', 'Portland', 'Boston', 'Salt Lake City', 'Milwaukee', 'Cheyenne',
                       'Fargo', 'Bethel']
        test_latitudes = [25.4479, 28.5383, 32.2217, 35.4676, 38.5816, 37.3382,
                          36.1627, 35.2220, 45.5231, 42.3600825, 40.7608, 43.0389, 41.1400,
                          46.8772, 60.7922]
        test_longitudes = [-80.479, -81.3792, -110.9265, -97.5164, -121.4944, -121.8863,
                           -86.7816, -101.8313, -122.6765, -71.0588801, -111.8910, -87.9065, -104.8202,
                           -96.7898, -161.7558]
        expected_ashrae_city = ['Miami', 'Houston', 'Phoenix', 'Atlanta', 'LosAngeles', 'SanFrancisco',
                                'Baltimore', 'Albuquerque', 'Seattle', 'Chicago', 'Boulder', 'Minneapolis',  'Helena',
                                'Duluth', 'Fairbanks']

        for i in range(0, len(test_cities)):
            profile = BuiltInProfile(test_latitudes[i], test_longitudes[i], "MidriseApartment", 500000)
            self.assertEqual(profile.city, expected_ashrae_city[i], {r"reopt": {"Error": "Incorrect ASHRAE city returned for test city: " + test_cities[i] + " Expected: " + expected_ashrae_city[i] + " Actual: " + profile.city}})


