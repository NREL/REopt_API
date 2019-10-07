import json
import os
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
from reo.nested_to_flat_output import nested_to_flat
#from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from reo.models import ModelManager
from reo.utilities import check_common_outputs


class NegativeLatitudeTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(NegativeLatitudeTest, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_souther_hemisphere_latitude(self):
        """
        Case with site exports greater than the cost of energy+demand+fixed charges. Expected outcome:
        - lcc for with_technology case negative
        - lcc for bau case positive
        ...
        - MinChargeAdder variable in the optimization formulation goes to zero
        :return:
        """

        nested_data = {'Scenario':{
                        'Site': {
                            'latitude':-31.9505,
                            'longitude':115.8605,
                            'ElectricTariff': {'urdb_label':'5b78d2775457a3bf45af0aed'},
                            'LoadProfile': {'doe_reference_name': 'Hospital',
                                            'annual_kwh':12000},
                            'Wind':{'max_kw':0},
                            'PV': {'array_type': 0}
                            }
                        }
                        }

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        messages = d['messages']

        try:
            self.assertEqual( d['inputs']['Scenario']['Site']['PV']['azimuth'], 0,
                             "Not adjusting azimuth for negative latitudes.")

            self.assertEqual(d['inputs']['Scenario']['Site']['PV']['tilt'], 31.9505,
                             "Not adjusting tilt for negative latitudes"
                             )

        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("NegativeLatitudeTest API error message: {}".format(error_msg))
            print("Run uuid: {}".format(d['outputs']['Scenario']['run_uuid']))
            raise e

