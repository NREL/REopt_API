import unittest
import requests
import random
import json
from annual_kwh.models import annual_loads, default_buildings, default_cities

server_url = "http://127.0.0.1:8000/annual_kwh"


class TestAnnualkWh(unittest.TestCase):

    def test_random_choice(self):
        """
        check a random building's expected annual_kwh
        """
        bldg = default_buildings[random.choice(range(len(default_buildings)))]
        city = default_cities[random.choice(range(len(default_cities)))]
        response = requests.get(server_url, params={
            'load_profile_name': bldg,
            'latitude': city.lat,
            'longitude': city.lng,
        })
        annual_kwh_from_api = json.loads(response.text).get('annual_kwh')
        assert annual_kwh_from_api == annual_loads[city.name][bldg]

    def test_bad_latitude(self):
        bldg = default_buildings[random.choice(range(len(default_buildings)))]
        city = default_cities[random.choice(range(len(default_cities)))]
        response = requests.get(server_url, params={
            'load_profile_name': bldg,
            'latitude': 'bad latitude',
            'longitude': city.lng,
        })
        assert "Exception Value: latitude or longitude contains invalid value. Please enter numeric value." \
               in response.iter_lines()

    def test_bad_building_name(self):
        bldg = default_buildings[random.choice(range(len(default_buildings)))]
        city = default_cities[random.choice(range(len(default_cities)))]
        response = requests.get(server_url, params={
            'load_profile_name': bldg[:-1],
            'latitude': city.lat,
            'longitude': city.lng,
        })
        assert "Exception Value: Invalid load_profile_name. Select from the following:" \
               in response.iter_lines()
