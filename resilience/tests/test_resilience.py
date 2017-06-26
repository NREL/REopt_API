import json
import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.api_definitions import *
from reo.validators import *
import numpy as np

class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(EntryResourceTest, self).setUp()

        self.required =  self.get_defaults_from_list(inputs(just_required=True))
        self.url_base = '/api/v1/reopt/'

    def get_defaults_from_list(self, list):
        base = {k: inputs(full_list=True)[k].get('default') for k in list}
        base['user_id'] = 'abc321'
        if 'load_8760_kw' in list:
            base['load_8760_kw'] = [0] * 8760
        if 'load_profile_name' in list:
            base['load_profile_name'] = default_load_profiles()[0]
        if 'latitude' in list:
            base['latitude'] = default_latitudes()[0]
        if 'longitude' in list:
            base['longitude'] = default_longitudes()[0]
        if 'urdb_rate' in list:
            base['urdb_rate'] = default_urdb_rate()
        if 'demand_charge' in list:
            base['demand_charge'] = default_demand_charge()
        if 'blended_utility_rate' in list:
            base['blended_utility_rate'] = default_blended_rate()
        return base

    def test_resilience_stats(self):

        data = self.required

        resp = self.api_client.post(self.url_base, format='json', data=data)
        print resp
        self.assertHttpCreated(resp)

        self.assertEqual(str(data['r_min']), str(0.02))
        self.assertEqual(str(data['r_max']), str(14.29))
        self.assertEqual(str(data['r_avg']), str(3.13))

        return

    def test_outage(self):
        return

    def test_no_system(self):
        return

    def test_pv_only(self):
        return

    def test_batt_only(self):
        return

    def test_batt_and_pv(self):
        return