# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.src.load_profile import BuiltInProfile, default_annual_electric_loads
import random
import json
from math import floor


class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(EntryResourceTest, self).setUp()
        self.annual_kwh_url = "/v1/annual_kwh/"
        self.default_building_types = [i for i in BuiltInProfile.default_buildings if i[0:8].lower() != 'flatload']

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
            self.assertEqual(floor(annual_kwh_from_api), floor(default_annual_electric_loads[city.name][bldg.lower()]), msg=msg)

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
