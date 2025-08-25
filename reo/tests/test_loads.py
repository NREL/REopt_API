# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
from django.test import TestCase
from reo.src.load_profile import BuiltInProfile

# Dummy commit to force master branch to redeploy fully 7/18/2025

class LoadsTestCase(TestCase):

    # mimic user passing in info
    def setUp(self):
        pass

    def test_ashrae_zones(self):

        test_cities = ['Florida City',  'Tucson', 'Oklahoma City', 'Sacremento', 'San Jose',
                       'Bowling Green', 'Amarillo', 'Portland', 'Boston', 'Salt Lake City', 'Green Bay', 'Casper',
                       'Grand Rapids', 'Bethel']
        test_latitudes = [25.4479,  32.2217, 35.4676, 38.5816, 37.3382,
                          36.9685, 35.2220, 45.5231, 42.3600825, 40.7608, 44.5133, 42.8501,
                          47.2372, 60.7922]
        test_longitudes = [-80.479, -110.9265, -97.5164, -121.4944, -121.8863,
                           -86.4808, -101.8313, -122.6765, -71.0588801, -111.8910, -88.0133, -106.3252,
                           -96.5302, -161.7558]
        expected_ashrae_city = ['Miami',  'Phoenix', 'Atlanta', 'LosAngeles', 'SanFrancisco',
                                'Baltimore', 'Albuquerque', 'Seattle', 'Chicago', 'Boulder', 'Minneapolis',  'Helena',
                                'Duluth', 'Fairbanks']

        for i in range(0, len(test_cities)):
            profile = BuiltInProfile(latitude=test_latitudes[i], longitude=test_longitudes[i], doe_reference_name="MidriseApartment", annual_energy=500000)
            self.assertEqual(profile.city, expected_ashrae_city[i], {r"reopt": {"Error": "Incorrect ASHRAE city returned for test city: " + test_cities[i] + " Expected: " + expected_ashrae_city[i] + " Actual: " + profile.city}})


