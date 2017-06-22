import json
import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.api_definitions import *
from reo.validators import *
import numpy as np

def u2s (d):
    sub_d = d['reopt']['Error']
    return {'reopt':{'Error':{str(k):[str(i) for i in v]  for k,v in sub_d.items()}}}

class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(EntryResourceTest, self).setUp()

        self.required  = inputs(just_required=True).keys()

        self.optional = [["urdb_rate"],["blended_utility_rate",'demand_charge']]

        self.url_base = '/api/v1/reopt/'

    def make_url(self,string):
        return self.url_base + string

    def get_defaults_from_list(self,list):
        base = {k:inputs(full_list=True)[k].get('default') for k in list}
        base['user_id'] = 'abc321'
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
    def list_to_default_string(self,list_inputs):
        output  = ""
        for f in list_inputs:
            output  += "&%s=%s" % (f,self.get_default(f))
        return output

    def request_swap_value(self,k,dummy_data,swaps,add):
        list = [i for i in self.required if i not in sum(swaps, [])] + add
        data = self.get_defaults_from_list(list)
        data[k] = dummy_data
        return self.api_client.post(self.url_base, format='json', data=data)

    def test_valid_swapping(self):
        swaps = [[['urdb_rate'],['demand_charge','blended_utility_rate']],[['load_profile_name'],['load_8760_kw']]]
        for sp in swaps:
            other_pairs = list(np.concatenate([i[0] for i in swaps if i!=sp ]))
            possible_messages = [{r"reopt":{"Error":{"Missing_Required": [REoptResourceValidation().get_missing_required_message(ii)]}}} for ii in sp[0]+sp[1]]
            for ss in sp:
                for f in ss:
                     dependent_fields = [i for i in ss if i != f]
                     l = [i for i in self.required if i not in sp[0]+sp[1] ] + dependent_fields + other_pairs
                     data = self.get_defaults_from_list(l)
                     resp = self.api_client.post(self.url_base, format='json', data=data) 
                     self.assertTrue(u2s(self.deserialize(resp)) in possible_messages )
    def test_required_fields(self):

        for f in self.required:
            swaps = inputs(full_list=True)['f'].get('swap_for')
            if swaps == None:
                swaps = []
            fields = [i for i in self.required if i != f and i not in swaps]
            data = self.get_defaults_from_list(fields)
            resp = self.api_client.post(self.url_base, format='json', data=data)
            self.assertEqual(u2s(self.deserialize(resp)), {r"reopt":{"Error":{"Missing_Required": [REoptResourceValidation().get_missing_required_message(f)]}}} )

    def test_dependent_fields(self):

        for f in inputs(full_list=True):
            if not bool(f.get('req')):
                if f.get('depends_on') is not None:
                    df = f.get('depends_on')
                fields = set( self.required + f ) - set(df)
                data = self.get_defaults_from_list(fields)
                resp = self.api_client.post(self.url_base, format='json', data=data)
                self.assertEqual(u2s(self.deserialize(resp)), {r"reopt": {"Error": {"Missing_Dependencies": [REoptResourceValidation().get_missing_dependency_message(f)]}}})

    def test_valid_test_defaults(self):

        '''
        # Come up with some new values, as model has changed


        swaps = [['urdb_rate'], ['demand_charge', 'blended_utility_rate']]

        for add in swaps:
            
            # Test All  Data and  Valid Rate Inputs
            data = {}
            data['user_id']="abc123"
            data['latitude'] = 25.7616798
            data['longitude'] = -80.19179020000001
            data['pv_om'] = 20
            data['batt_cost_kw'] = 1600
            data['batt_cost_kwh'] = 500
            data['pv_cost'] = 2160
            data['owner_discount_rate'] = 8
            data['offtaker_discount_rate'] = 8

	    if add == ['urdb_rate']:
                data['load_size'] = 10000000
                data['urdb_rate'] = default_urdb_rate()
                data['load_profile_name'] = 'Hospital'
            else:
                data['load_monthly_kwh'] = default_load_monthly()
                data['blended_utility_rate'] = default_blended_rate()
                data['demand_charge'] = default_demand_charge()                    


   
            resp = self.api_client.post(self.url_base, format='json', data=data)
            self.assertHttpCreated(resp)
            
            if add != ['urdb_rate']:
                d = json.loads(resp.content)
                self.assertEqual(str(d['lcc']),'1973.33')
                self.assertEqual(str(d['npv']),'0.0')
                self.assertEqual(str(d['pv_kw']),'0')
                self.assertEqual(str(d['batt_kw']),'0.0')
                self.assertEqual(str(d['batt_kwh']),'0.0')
                self.assertEqual(str(d['utility_kwh']),'3400.0')
            
            if add == ['urdb_rate']:
                d = json.loads(resp.content)
                self.assertEqual(str(d['lcc']),str(8413330.0))
                self.assertEqual(str(d['npv']),str(12250.0))
                self.assertEqual(str(d['pv_kw']),str(59.0))
                self.assertEqual(str(d['batt_kw']),str(28.1348))
                self.assertEqual(str(d['batt_kwh']),str(54.9747))
                self.assertEqual(int(float(d['utility_kwh'])),9978797)
        '''

    def test_valid_data_types(self):
        swaps = [['urdb_rate'], ['demand_charge', 'blended_utility_rate']]
        for add in swaps:
            # Test Bad Data Types
            for k,v in inputs(just_required=True).items():
                dummy_data = 1
                if v['type'] in [float,int]:
                    dummy_data  = u"A"
                resp = self.request_swap_value(k, dummy_data, swaps, add)
                self.assertEqual(u2s(self.deserialize(resp)), {r"reopt": {"Error": {k: ['Invalid format: Expected %s, got %s'%(v['type'].__name__, type(dummy_data).__name__)]}}})

    def test_valid_data_ranges(self):
        swaps = [['urdb_rate'], ['demand_charge', 'blended_utility_rate']]
        for add in swaps:
            # Test Bad Data Types
            checks  = set(['min','max','minpct','maxpct','restrict'])
            completed_checks = []

            while completed_checks != checks:
                for k, v in inputs(just_required=True).items():

                    if v.get('min') is not None and v.get('pct') is not True:
                        dummy_data =  -1000000
                        resp = self.request_swap_value(k,dummy_data,swaps,add)
                        self.assertEqual(u2s(self.deserialize(resp)), {
                            r"reopt": {"Error": {k: ['Invalid value: %s is less than the minimum, %s' % (dummy_data, v.get('min'))]}}})
                        completed_checks = set(list(completed_checks) + ['min'])

                    if v.get('max') is not None and v.get('pct') is not True:
                        dummy_data = 1000000
                        resp = self.request_swap_value(k, dummy_data, swaps, add)
                        self.assertEqual(u2s(self.deserialize(resp)), {
                            r"reopt": {"Error": {k: ['Invalid value: %s is greater than the  maximum, %s' % (dummy_data, v.get('max'))]}}})
                        completed_checks = set(list(completed_checks) + ['max'])

                    if v.get('min') is not None and bool(v.get('pct')):
                        dummy_data =  -1000000
                        resp = self.request_swap_value(k, dummy_data, swaps, add)
                        self.assertEqual(u2s(self.deserialize(resp)), {
                            r"reopt": {"Error": {
                                k: ['Invalid value: %s is less than the minimum, %s %%' % (dummy_data, v.get('min')*100)]}}})
                        completed_checks = set(list(completed_checks) + ['minpct'])

                    if v.get('max') is not None and bool(v.get('pct')):
                        dummy_data = 1000000
                        resp = self.request_swap_value(k, dummy_data, swaps, add)
                        self.assertEqual(u2s(self.deserialize(resp)), {
                            r"reopt": {"Error": {
                                k: ['Invalid value: %s is greater than the  maximum, %s %%' % (dummy_data, v.get('max')*100)]}}})
                        completed_checks = set(list(completed_checks) + ['maxpct'])

                    if bool(v.get('restrict_to')):
                        if v.get('type') in [int,float]:
                            dummy_data = -123
                        else:
                            dummy_data  =  "!@#$%^&*UI("

                        resp = self.request_swap_value(k, dummy_data, swaps, add)
                        self.assertEqual(u2s(self.deserialize(resp)), {
                            r"reopt": {
                                "Error": {k: ['Invalid value: %s is not in %s' % (dummy_data, v.get('restrict_to'))]}}})
                        completed_checks = set(list(completed_checks) + ['restrict'])

                completed_checks = set(checks)
