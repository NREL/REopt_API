import time
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
                          "latitude": 35.2468,
                          "longitude": -91.7337,

                          "LoadProfile": {
                            "doe_reference_name": "MidriseApartment",
                            "year": 2017,
                          },

                          "ElectricTariff": {
                            "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
                          },

                          "PV": {
                            "existing_kw": "100",
                          },
                        "Wind": {
                            "max_kw": 0,
                            },
                          "Storage": {
                              "max_kw": 0,
                              "max_kwh": 0,
                          }
                        }
                      }
                    }

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
        Pass in existing PV size = PV max_kw and verify that:
        - sized system is existing_kw
        - zero capital costs (battery size set to zero)
        - npv is zero (i.e. same benefits in BAU with existing PV as in cost-optimal scenario.)

        Also pass in PV array type as 0 (ground mount fixed) and verify that:
        - the default tilt angle gets set equal to the latitude (given that 'tilt' is not provided as input)
        ...
        - production incentives applied to existing PV
        """

        class ClassAttributes:
            def __init__(self, dictionary):
                for k, v in dictionary.items():
                    setattr(self, k, v)

        pv_size = 100
        existing_kw = pv_size
        max_kw = pv_size
        flat_load = [pv_size] * 8760

        self.post['Scenario']['Site']['PV']['existing_kw'] = existing_kw
        self.post['Scenario']['Site']['PV']['max_kw'] = max_kw
        self.post['Scenario']['Site']['PV']['array_type'] = 0
        self.post['Scenario']['Site']['LoadProfile']['loads_kw_is_net'] = True
        self.post['Scenario']['Site']['LoadProfile']['loads_kw'] = flat_load

        response = self.get_response(self.post)
        pv_out = ClassAttributes(response['outputs']['Scenario']['Site']['PV'])
        load_out = ClassAttributes(response['outputs']['Scenario']['Site']['LoadProfile'])
        financial = ClassAttributes(response['outputs']['Scenario']['Site']['Financial'])
        latitude_input = response['inputs']['Scenario']['Site']['latitude']
        tilt_out = response['inputs']['Scenario']['Site']['PV']['tilt']
        messages = ClassAttributes(response['messages'])

        net_load = [a - round(b,3) for a, b in zip(load_out.year_one_electric_load_series_kw, pv_out.year_one_power_production_series_kw)]
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

            self.assertEqual(tilt_out, latitude_input,
                             "Tilt default should be equal latitude for ground-mount fixed array_type input")

            # self.assertListEqual(flat_load, net_load)  # takes forever!
            zero_list = [round(a - b, 2) for a, b in zip(flat_load, net_load)]
            zero_sum = sum(zero_list)
            self.assertEqual(zero_sum, 0, "Net load is not being calculated correctly.")

        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("test_existing_pv API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e
