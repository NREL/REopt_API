import json
import os
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class TestExistingPV(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestExistingPV, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        post_file = os.path.join('reo', 'tests', 'nestedPOST.json')
        self.post = json.load(open(post_file, 'r'))

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        uuid = json.loads(initial_post.content)['run_uuid']

        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)

        # # the following is not needed b/c we test the app with Celery tasks in "eager" mode
        # # i.e. asynchronously. If we move to testing the API, then the while loop is needed
        # status = response['outputs']['Scenario']['status']
        # while status == "Optimizing...":
        #     time.sleep(2)
        #     response = json.loads(self.api_client.get(self.results_url + uuid).content)
        #     status = response['outputs']['Scenario']['status']

        return response

    def test_existing_pv(self):
        """
        Pass in existing PV size and verify that sized system is at least that big
        """

        class ClassAttributes:
            def __init__(self, dictionary):
                for k, v in dictionary.items():
                    setattr(self, k, v)

        existing_kw = 100
        max_kw = 100
        flat_load = [1] * 8760

        load_is_net = True
        self.post['Scenario']['Site']['PV']['existing_kw'] = existing_kw
        self.post['Scenario']['Site']['PV']['max_kw'] = max_kw
        self.post['Scenario']['Site']['LoadProfile']['loads_kw_is_net'] = True
        #self.post['Scenario']['Site']['LoadProfile']['loads_kw'] = flat_load

        response = self.get_response(self.post)
        pv_out = ClassAttributes(response['outputs']['Scenario']['Site']['PV'])
        load_out = ClassAttributes(response['outputs']['Scenario']['Site']['LoadProfile'])


        #net_load = [a - b for a, b in zip(load_out.year_one_electric_load_series_kw, pv_out.year_one_power_production_series_kw)]


        self.assertGreaterEqual(existing_kw, pv_out.size_kw)
        #self.assertListEqual(flat_load, net_load)



