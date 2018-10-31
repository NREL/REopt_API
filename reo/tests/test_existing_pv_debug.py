import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class TestExistingPV(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestExistingPV, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = {"Scenario": {
                        "Site": {
                          "latitude": 34.5794343,
                          "longitude": -118.11646129999997,

                          "LoadProfile": {
                            "doe_reference_name": "RetailStore",
                            "year": 2017,
                          },

                          "ElectricTariff": {
                            "urdb_utility_name":"City of Glendale, California (Utility Company)",
                            "urdb_rate_name":"Residential L-1-A Standard Service Rate",

                          },

                          "PV": {
                            "existing_kw": 1000,
                          },
                        }
                      }
                    }

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        #uuid = json.loads(initial_post.content)['outputs']['Scenario']['run_uuid']
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
        Pass in existing PV size = PV max_kw and verify that:
        - sized system is existing_kw
        - zero capital costs (battery size set to zero)
        - npv is zero (i.e. same benefits in BAU with existing PV as in cost-optimal scenario.)
        ...
        - production incentives applied to existing PV
        """

        class ClassAttributes:
            def __init__(self, dictionary):
                for k, v in dictionary.items():
                    setattr(self, k, v)

        pv_size = 1000
        existing_kw = pv_size


        self.post['Scenario']['Site']['PV']['existing_kw'] = existing_kw


        response = self.get_response(self.post)
        pv_out = ClassAttributes(response['outputs']['Scenario']['Site']['PV'])
        load_out = ClassAttributes(response['outputs']['Scenario']['Site']['LoadProfile'])
        financial = ClassAttributes(response['outputs']['Scenario']['Site']['Financial'])
        messages = ClassAttributes(response['messages'])


        try:
            self.assertEqual(existing_kw, pv_out.size_kw,
                             "Existing PV size ({} kW) does not equal REopt PV size ({} kW)."
                             .format(pv_size, pv_out.size_kw))

            self.assertEqual(financial.net_capital_costs, 0,
                             "Non-zero capital cost for existing PV: {}."
                             .format(financial.net_capital_costs))

            self.assertEqual(financial.npv_us_dollars, 0,
                             "Non-zero NPV with existing PV in both BAU and cost-optimal scenarios: {}."
                             .format(financial.npv_us_dollars))



        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("test_existing_pv API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e
