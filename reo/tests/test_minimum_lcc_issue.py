import time
import json
import os
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
from reo.nested_to_flat_output import nested_to_flat
#from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from reo.models import ModelManager
from reo.utilities import check_common_outputs


class MinimumLccTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(MinimumLccTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_negative_lcc(self):
        """
        Case with site exports greater than the cost of energy+demand+fixed charges. Expected outcome:
        - lcc for with_technology case negative
        - lcc for bau case positive
        ...
        - MinChargeAdder variable in the optimization formulation goes to zero
        :return:
        """
        test_post = os.path.join('reo', 'tests', 'minimum_lcc_issue1.json')
        nested_data = json.load(open(test_post, 'rb'))

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        

        c = nested_to_flat(d['outputs'])

        lcc_bau = d['outputs']['Scenario']['Site']['Financial']['lcc_bau_us_dollars']
        lcc = d['outputs']['Scenario']['Site']['Financial']['lcc_us_dollars']
        messages = d['messages']

        try:
            self.assertGreater(lcc_bau, 0,
                             "BAU Life Cycle Cost is less than zero. This is not correct.")

            self.assertLess(lcc, 0,
                             "non-negative LCC cost for the case when site exports are greater than net energy import costs."
                             )

        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("test_negative_lcc API error message: {}".format(error_msg))
            print("Run uuid: {}".format(d['outputs']['Scenario']['run_uuid']))
            raise e

    def test_positive_lcc(self):
        """
        Case with site exports more than the cost of energy+demand+fixed charges.
        Utility imposes a total minimum monthly charge as well fixed monthly charge.
        Expected outcome:
        - lcc for both the cases positive
        ...
        - MinChargeAdder variable in the optimization formulation is expected to become positive
        :return:
        """
        test_post = os.path.join('reo', 'tests', 'minimum_lcc_issue2.json')
        nested_data = json.load(open(test_post, 'rb'))


        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        
        c = nested_to_flat(d['outputs'])
        
        lcc_bau = d['outputs']['Scenario']['Site']['Financial']['lcc_bau_us_dollars']
        lcc = d['outputs']['Scenario']['Site']['Financial']['lcc_us_dollars']
        messages = d['messages']

        try:

            self.assertGreater(lcc_bau, 0,
                             "BAU Life Cycle Cost is less than zero. This is not correct.")

            self.assertGreater(lcc, 0,
                             "the lcc should be positive for this case, given the test inputs. "
                             )

        except Exception as e:
            
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("test_positive_lcc API error message: {}".format(error_msg))
            print("Run uuid: {}".format(d['outputs']['Scenario']['run_uuid']))
            raise e