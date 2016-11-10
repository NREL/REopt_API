import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.api_definitions import *
from reo.validators import *

class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(EntryResourceTest, self).setUp()

        self.required  = ["latitude","longitude","pv_om","batt_cost_kw",
                          "batt_cost_kwh","pv_cost", "owner_discount_rate","offtaker_discount_rate"]

        self.optional = [["urdb_rate"],["blended_utility_rate",'demand_charge']]

        self.url_base = '/api/v1/reopt/'

    def make_url(self,string):
        return self.url_base + string

    def get_defaults_from_list(self,list):
        return {k:inputs(full_list=True)[k]['default'] for k in list}

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

    def test_valid_inputs(self):
        swaps = [['urdb_rate'],['demand_charge','blended_utility_rate']]
        for add in swaps :
            #Test  Requiring Inputs
            for f in self.required:
                l = [i for i in self.required if i!=f and i not in sum(swaps, []) ] + add
                data = self.get_defaults_from_list(l)
                resp = self.api_client.post(self.url_base, format='json', data=data)
                f =  REoptResourceValidation().get_missing_required_message(f)
                self.assertEqual(self.deserialize(resp), {r"reopt":{"Error:":{"Missing_Required":[f]}}} )

    def test_valid_test_defaults(self):
        swaps = [['urdb_rate'], ['demand_charge', 'blended_utility_rate']]
        for add in swaps:
            # Test All  Data and  Valid Rate Inputs
            data = self.get_defaults_from_list(self.required + add)
            data['user_id']="abc123"
            resp = self.api_client.post(self.url_base, format='json', data=data)
            self.assertHttpCreated(resp)

    def test_valid_data_types(self):
        swaps = [['urdb_rate'], ['demand_charge', 'blended_utility_rate']]
        for add in swaps:
            # Test Bad Data Types
            for k,v in inputs(just_required=True).items():
                dummy_data = 1
                if v['type'] in [float,int]:
                    dummy_data  = u"A"
                resp = self.request_swap_value(k, dummy_data, swaps, add)
                self.assertEqual(self.deserialize(resp), {r"reopt": {"Error:": {k: ['Invalid format: Expected %s, got %s'%(v['type'], type(dummy_data))]}}})

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
                        self.assertEqual(self.deserialize(resp), {
                            r"reopt": {"Error:": {k: ['Invalid value: %s is less than the minimum, %s' % (dummy_data, v.get('min'))]}}})
                        completed_checks = set(list(completed_checks) + ['min'])

                    if v.get('max') is not None and v.get('pct') is not True:
                        dummy_data = 1000000
                        resp = self.request_swap_value(k, dummy_data, swaps, add)
                        self.assertEqual(self.deserialize(resp), {
                            r"reopt": {"Error:": {k: ['Invalid value: %s is greater than the  maximum, %s' % (dummy_data, v.get('max'))]}}})
                        completed_checks = set(list(completed_checks) + ['max'])

                    if v.get('min') is not None and bool(v.get('pct')):
                        dummy_data =  -1000000
                        resp = self.request_swap_value(k, dummy_data, swaps, add)
                        self.assertEqual(self.deserialize(resp), {
                            r"reopt": {"Error:": {
                                k: ['Invalid value: %s is less than the minimum, %s %%' % (dummy_data, v.get('min')*100)]}}})
                        completed_checks = set(list(completed_checks) + ['minpct'])

                    if v.get('max') is not None and bool(v.get('pct')):
                        dummy_data = 1000000
                        resp = self.request_swap_value(k, dummy_data, swaps, add)
                        self.assertEqual(self.deserialize(resp), {
                            r"reopt": {"Error:": {
                                k: ['Invalid value: %s is greater than the  maximum, %s %%' % (dummy_data, v.get('max')*100)]}}})
                        completed_checks = set(list(completed_checks) + ['maxpct'])

                    if bool(v.get('restrict_to')):
                        if v.get('type') in [int,float]:
                            dummy_data = -123
                        else:
                            dummy_data  =  "!@#$%^&*UI("

                        resp = self.request_swap_value(k, dummy_data, swaps, add)
                        self.assertEqual(self.deserialize(resp), {
                            r"reopt": {
                                "Error:": {k: ['Invalid value: %s is not in %s' % (dummy_data, v.get('restrict_to'))]}}})
                        completed_checks = set(list(completed_checks) + ['restrict'])

                completed_checks = set(checks)