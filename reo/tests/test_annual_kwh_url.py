from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.src.load_profile import BuiltInProfile
import random
import json

class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(EntryResourceTest, self).setUp()
        self.annual_kwh_url = "/reopt/annual_kwh/"

    def test_annual_kwh_random_choice(self):
        """
        check a random building's expected annual_kwh
        """
        bldg = BuiltInProfile.default_buildings[random.choice(range(len(BuiltInProfile.default_buildings)))]
        city = BuiltInProfile.default_cities[random.choice(range(len(BuiltInProfile.default_cities)))]
        response = self.api_client.get(self.annual_kwh_url, data={
            'doe_reference_name': bldg,
            'latitude': city.lat,
            'longitude': city.lng,
        })
       
        annual_kwh_from_api = json.loads(response.content).get('annual_kwh')
        assert annual_kwh_from_api == BuiltInProfile.annual_loads[city.name][bldg]
   

    def test_annual_kwh_bad_latitude(self):
        bldg = BuiltInProfile.default_buildings[random.choice(range(len(BuiltInProfile.default_buildings)))]
        city = BuiltInProfile.default_cities[random.choice(range(len(BuiltInProfile.default_cities)))]
       
        response = self.api_client.get(self.annual_kwh_url, data={
            'doe_reference_name': bldg,
            'latitude': 'bad latitude',
            'longitude': city.lng,
        })

        assert "could not convert string to float" in response.content

    def test_annual_kwh_bad_building_name(self):
        bldg = BuiltInProfile.default_buildings[random.choice(range(len(BuiltInProfile.default_buildings)))]
        city = BuiltInProfile.default_cities[random.choice(range(len(BuiltInProfile.default_cities)))]

        response = self.api_client.get(self.annual_kwh_url, data={
            'doe_reference_name': bldg[:-1],
            'latitude': city.lat,
            'longitude': city.lng,
        })

        assert "Invalid doe_reference_name. Select from the following" in response.content
