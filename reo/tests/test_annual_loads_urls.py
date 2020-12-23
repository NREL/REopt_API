from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.src.load_profile import LoadProfile, BuiltInProfile, default_annual_electric_loads
from reo.src.load_profile_boiler_fuel import LoadProfileBoilerFuel  
import random
import json


class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(EntryResourceTest, self).setUp()
        self.annual_kwh_url = "/v1/annual_kwh/"
        self.annual_mmbtu_url = "/v1/annual_mmbtu/"
        self.default_building_types = [i for i in BuiltInProfile.default_buildings if i.lower() !='flatload']

    def test_annual_kwh_random_choice(self):
        """
        check a random city's expected annual_kwh (for each building)
        """
        city = BuiltInProfile.default_cities[random.choice(range(len(BuiltInProfile.default_cities)))]
        for bldg in self.default_building_types:
            response = self.api_client.get(self.annual_kwh_url, data={
                'doe_reference_name': bldg,
                'latitude': city.lat,
                'longitude': city.lng,
            })
            annual_kwh_from_api = json.loads(response.content).get('annual_kwh')
            msg = "Loads not equal for: " + str(bldg) + " city 1: " + str(city.name) + " city 2: " + str(json.loads(response.content).get('city'))
            self.assertEqual(round(annual_kwh_from_api, 0), round(default_annual_electric_loads[city.name][bldg.lower()], 0), msg=msg)

    def test_annual_mmbtu_random_choice(self):
        """
        check a random city's expected annual_mmbtu heating load (for each building)
        """
        city = BuiltInProfile.default_cities[random.choice(range(len(BuiltInProfile.default_cities)))]
        for bldg in self.default_building_types:
            response = self.api_client.get(self.annual_mmbtu_url, data={
                'doe_reference_name': bldg,
                'latitude': city.lat,
                'longitude': city.lng,
            })
            annual_mmbtu_from_api = json.loads(response.content).get('annual_mmbtu')
            msg = "Loads not equal for: " + str(bldg) + " city 1: " + str(city.name) + " city 2: " + str(json.loads(response.content).get('city'))
            self.assertEqual(round(annual_mmbtu_from_api, 0), round(LoadProfileBoilerFuel.annual_loads[city.name][bldg.lower()], 0), msg=msg)

    def test_annual_kwh_bad_latitude(self):
        bldg = self.default_building_types[random.choice(range(len(self.default_building_types)))]

        city = BuiltInProfile.default_cities[random.choice(range(len(BuiltInProfile.default_cities)))]
       
        response = self.api_client.get(self.annual_kwh_url, data={
            'doe_reference_name': bldg,
            'latitude': 'bad latitude',
            'longitude': city.lng,
        })

        assert "could not convert string to float" in str(response.content)

    def test_annual_kwh_bad_building_name(self):
        bldg = self.default_building_types[random.choice(range(len(self.default_building_types)))]

        city = BuiltInProfile.default_cities[random.choice(range(len(BuiltInProfile.default_cities)))]

        response = self.api_client.get(self.annual_kwh_url, data={
            'doe_reference_name': bldg[:-1],
            'latitude': city.lat,
            'longitude': city.lng,
        })

        assert "Invalid doe_reference_name {}. Select from the following".format(bldg[:-1]) in str(response.content)
