import json
from tastypie.test import ResourceTestCaseMixin
from reo.nested_inputs import nested_input_definitions
from reo.nested_to_flat_output import nested_to_flat
from unittest import TestCase, skip  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from reo.models import ModelManager
from reo.nested_inputs import flat_to_nested
from reo.utilities import check_common_outputs
from functools import reduce  # forward compatibility for Python 3
import operator
import copy


def get_by_path(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)


def remove_by_path(root, items):
    """Remove a value in a nested object in root by item sequence."""
    del get_by_path(root, items[:-1])[items[-1]]


class TestJumpModel(ResourceTestCaseMixin, TestCase):

    REopt_tol = 1e-2

    @classmethod
    def setUpClass(cls):
        super(TestJumpModel, cls).setUpClass()
        cls.data_definitions = nested_input_definitions
        cls.reopt_base = '/v1/job/'
        cls.nested_post = json.load(open('reo/tests/posts/nestedPOST.json'))

    @property
    def complete_valid_nestedpost(self):
        return copy.deepcopy(self.nested_post)

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def check_data_error_response(self, data, text):
        response = self.get_response(data)
        self.assertTrue(text in response.content)

    def get_inputs_with_sub_key_from_nested_dict(self, nested_dict, sub_key, matched_values=None, obj_path=[],
                                                 sub_key_values=[]):
        """
        given a nested dictionary (i.e. nested_inputs_definitions) return all of the keys that contain sub-keys matching
        sub_key
        :param nested_dict:
        :param sub_key:
        :param matched_values: list of str containing desired keys
        :param obj:
        :return:
        """
        if matched_values is None:
            matched_values = []
        for k, v in nested_dict.items():
            if k[0].islower() and isinstance(v, dict):  # then k is an input attribute
                if any(sk == sub_key for sk in nested_dict[k].keys()):
                    matched_values.append(obj_path + [k])
                    sub_key_values.append(nested_dict[k][sub_key])
            elif isinstance(nested_dict[k], dict):  # then k is an abstract input class, dig deeper in nested_dict
                self.get_inputs_with_sub_key_from_nested_dict(nested_dict[k], sub_key, matched_values,
                                                              obj_path=obj_path+[k])
        return matched_values, sub_key_values

    def test_jump_with_no_techs(self):
        """
        Initial test for running Julia as Celery Task
        """
        post = {"Scenario": {"Site": {
                                "PV": {
                                    "max_kw": 0,
                                },
                                "Generator": {
                                    "max_kw": 0,
                                },
                                "LoadProfile": {
                                    "year": 2018,
                                    "annual_kwh": 100000.0,
                                    "doe_reference_name": "Hospital"
                                },
                                "ElectricTariff": {
                                    "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                                    "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
                                },
                                "longitude": -118.0,
                                "latitude": 34.5794343,
                                "Wind" : {
                                    "max_kw": 0
                                },
                                "Storage": {
                                    "max_kw": 0
                                }
        }}}

        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        d = ModelManager.make_response(run_uuid=r.get('run_uuid'))

        c = nested_to_flat(d['outputs'])

        d_expected = dict()
        d_expected['lcc'] = 178929
        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(r.get('run_uuid')))
            print("Error message: {}".format(d['messages']))
            raise

    @skip("Won't actually time-out until we solve a real problem")
    def test_jump_timeout(self):
        """
        Initial test for running Julia as Celery Task
        """
        post = {"Scenario": {
                    "timeout_seconds": 1,
                    "Site": {
                        "PV": {
                            "max_kw": 0,
                        },
                        "Generator": {
                            "max_kw": 0,
                        },
                        "LoadProfile": {
                            "year": 2018,
                            "annual_kwh": 100000.0,
                            "doe_reference_name": "Hospital"
                        },
                        "ElectricTariff": {
                            "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
                        },
                        "longitude": -118.0,
                        "latitude": 34.5794343,
                        "Wind" : {
                            "max_kw": 0
                        },
                        "Storage": {
                            "max_kw": 0
                        }
                    }
                }
        }
        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        results = ModelManager.make_response(run_uuid=r.get('run_uuid'))
        self.assertTrue('Optimization exceeded timeout: 1 seconds.' in results['messages']['error'])


