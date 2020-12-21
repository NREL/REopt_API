import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
import logging
logging.disable(logging.CRITICAL)


class ClassAttributes:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)


class TestNegativeNetLoad(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestNegativeNetLoad, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        with open('reo/tests/posts/nestedPOST.json') as f:
            self.post = json.loads(f.read())
        

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        uuid = json.loads(initial_post.content)['run_uuid']
        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
        return response

    def test_negative_net_load(self):
        """
        Test that self.post scenario, with monthly rates, returns the expected LCC and PV station attributes
        """
        self.post['Scenario']['Site']['LoadProfile']['loads_kw'] = [1 for _ in range(8760)]
        self.post['Scenario']['Site']['LoadProfile']['loads_kw'][10] = -1
        del self.post['Scenario']['Site']['LoadProfile']['doe_reference_name']
        del self.post['Scenario']['Site']['LoadProfile']['annual_kwh']
        del self.post['Scenario']['Site']['LoadProfile']['year']
        del self.post['Scenario']['Site']['LoadProfile']['monthly_totals_kwh']
        del self.post['Scenario']['Site']['LoadProfile']['outage_start_time_step']
        del self.post['Scenario']['Site']['LoadProfile']['outage_end_time_step']
        del self.post['Scenario']['Site']['LoadProfile']['critical_load_pct']
        del self.post['Scenario']['Site']['LoadProfile']['critical_loads_kw']

        response = self.get_response(self.post)

        self.assertTrue("After adding existing generation to the load profile there were still negative electricity loads. Loads (non-net) must be equal to or greater than 0." in response['messages']['error'])