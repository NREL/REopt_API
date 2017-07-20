import json
import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from tastypie.models import ApiKey
from reo.api_definitions import *
from reo.validators import *
import numpy as np
import pickle

class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(EntryResourceTest, self).setUp()

        self.required =  self.get_defaults_from_list(inputs(just_required=True))
     
        self.base_case_1 = {k:v for k,v in self.required.items() if k not in ['load_8760_kw', 'blended_utility_rate','demand_charge']}
        self.base_case_1['load_size'] = 10000	

        self.url_base = '/api/v1/reopt/'

    def get_defaults_from_list(self, list):
        base = {k: inputs(full_list=True)[k].get('default') for k in list}
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

    def expected_base_case_1(self):
        return pickle.load(open('resilience/tests/base_case_1','r'))

    def get_response(self, data):

        resp = self.api_client.post(self.url_base, format='json', data=data)
        self.assertHttpCreated(resp)
        d = self.deserialize(resp)

        return d

    def test_base_case_1(self):
        d = self.get_response(self.base_case_1)
        expected_result = self.expected_base_case_1()


        for f in ['resilience_hours_min','resilience_hours_max','resilience_hours_avg','resilience_by_timestep']:
             self.assertEqual(d[f], expected_result[f])
        
        return

    def test_outage(self):
        data = self.base_case_1
        data['outage_start'] = 100 
        data['outage_end'] = 110

        d = self.get_response(data)
   
        self.assertTrue(d['resilience_hours_max']>=10)
        for i in range(100,110):
            self.assertTrue(d['resilience_by_timestep'][i]>1)

    def test_no_system(self):
        data = self.base_case_1
        data['pv_kw_max'] = 0
        data['batt_kwh_max'] = 0
    
        d = self.get_response(data)
        self.assertEqual(int(d['resilience_hours_max']), 0)
        self.assertEqual(int(d['resilience_hours_min']), 0)

        for i in d['resilience_by_timestep']:
            self.assertEqual(i, 0)

        return

    def test_pv_only(self):
        data = self.base_case_1
        data['batt_kwh_max'] = 0
        data['load_profile_name']='RetailStore'
        data['blended_utility_rate'] = [0.25]*12
        data['demand_charge'] = [0.25]*12
        del data['urdb_rate']

        d = self.get_response(data)

        self.assertEqual(int(d['resilience_hours_max']), 13)
        self.assertEqual(int(d['resilience_hours_min']), 0)

        for i in d['resilience_by_timestep']:
            self.assertTrue(i<15)

        for i in d['resilience_by_timestep'][0::24]:
            self.assertTrue(i==0)

        return

    def test_batt_only(self):
        data = self.base_case_1
        data['pv_kw_max'] = 0
        data['blended_utility_rate'] = [1000]*12
        data['demand_charge'] = [1000]*12
        del data['urdb_rate']

        d = self.get_response(data)
    
        load = d['year_one_electric_load_series']
        max_load = max(load)

        for i,l in enumerate(load):
             l = l * d['crit_load_factor']
             if l > d['batt_kwh']*d['year_one_battery_soc_series'][i] or l > d['batt_kw']:
                 self.assertTrue(d['resilience_by_timestep'][i] < 1)
             elif l < d['batt_kwh']  and l < d['batt_kw']:
                 self.assertTrue(d['resilience_by_timestep'][i] > 1)

        return
