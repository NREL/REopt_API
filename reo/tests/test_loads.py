import os
from django.test import TestCase
from reo.src.load_profile import BuiltInProfile


class LoadsTestCase(TestCase):

    # mimic user passing in info
    def setUp(self):
        print "Nothing to do"

    def test_ashrae_zones(self):

        # test Boston, is within Chicago ASHRAE zone
        Boston = BuiltInProfile(42.3600825, -71.0588801, "MidriseApartment", 500000)
        self.assertEqual(Boston.city, "Chicago", {r"reopt": {"Error": "Incorrect ASHRAE city returned"}})



