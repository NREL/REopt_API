import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.api_definitions import *


class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(EntryResourceTest, self).setUp()

        self.required  = ["latitude","longitude","pv_om","batt_cost_kw",
                          "batt_cost_kwh","pv_cost", "owner_discount_rate","offtaker_discount_rate"]

        self.optional = [["urdb_rate"],["blended_utility_rate",'demand_charge']]

        self.url_base = "api/v1/reopt/?format=json"

    def make_url(self,string):
        return self.url_base + string

    def get_default(self,field):
        return inputs(full_list=True)[field]['default']

    def list_to_default_string(self,list_inputs):
        output  = ""
        for f in list_inputs:
            output  += "&%s=%s" % (f,self.get_default(f))
        return output

    def test_required(self):
        for f in self.required:
            list = [i for i in  self.required if i!=f] + ['urdb_rate']
            test_string = self.list_to_default_string(list)
            url = self.make_url(test_string)
            print test_string
            resp = self.api_client.get(url, format='json')
            self.assertValidJSONResponse(resp)
            self.assertEqual(self.deserialize(resp)['Error'], 'Missing  Required Field :' + f )

        for f in self.required:
            list = [i for i in self.required if i != f] + ['demand_charge','blended_utility_rate']
            test_string = self.list_to_default_string(list)
            url = self.make_url(test_string)
            print test_string
            resp = self.api_client.get(url, format='json')
            self.assertValidJSONResponse(resp)
            self.assertEqual(self.deserialize(resp)['Error'], 'Missing  Required Field :' + f)
