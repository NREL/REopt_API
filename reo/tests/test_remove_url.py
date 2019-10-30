import json
import pickle
from tastypie.test import ResourceTestCaseMixin
from reo.nested_inputs import nested_input_definitions
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from reo.models import  ScenarioModel


class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    REopt_tol = 1e-2

    def setUp(self):
        super(EntryResourceTest, self).setUp()

        self.data_definitions = nested_input_definitions
        self.reopt_base = '/v1/job/'
        self.missing_rate_urdb = pickle.load(open('reo/tests/missing_rate.p','rb'))
        self.missing_schedule_urdb = pickle.load(open('reo/tests/missing_schedule.p','rb'))

    @property
    def complete_valid_nestedpost(self):
        return json.load(open('reo/tests/posts/nestedPOST.json'))

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_required(self):
        test_case = self.complete_valid_nestedpost
        resp = self.get_response(test_case)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        response = self.api_client.get(self.reopt_base + str(run_uuid) + '/remove')
        self.assertEqual(response.status_code, 204)
        self.assertTrue(len(ScenarioModel.objects.filter(run_uuid=run_uuid)) == 0)
