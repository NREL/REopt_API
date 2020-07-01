import json
import copy
import os
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat_chp
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from unittest import skip
from reo.models import ModelManager
from reo.utilities import check_common_outputs
from reo.validators import ValidateNestedInput


class CHPTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(CHPTest, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_post = os.path.join('reo', 'tests', 'posts', 'test_chp_sizing_POST.json')
        #self.test_post = os.path.join('reo', 'tests', 'posts', 'POST_test_chp_OS.json')

    def get_response(self, data):

        return self.api_client.post(self.reopt_base, format='json', data=data)

    #@skip("CHP test")
    def test_chp_sizing(self):
        """
        Validation to ensure that:
         1) CHP Sizing is consistent

         This test was verified to be withing 1.5% gap after 10 mins of the Mosel/Xpress monolith using windows Xpress IVE

        :return:
        """

        # Call API, get results in "d" dictionary
        nested_data = json.load(open(self.test_post, 'rb'))
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat_chp(d['outputs'])
        from celery.contrib import rdb
        rdb.set_trace()
        # This test was verified to be withing 1.5% gap after 10 mins of the Mosel/Xpress monolith
        d_expected = dict()
        d_expected['lcc'] = 13406752.0
        d_expected['npv'] = 1412341.0
        d_expected['chp_kw'] = 776.94
        d_expected['chp_year_one_fuel_used_mmbtu'] = 42065.37
        d_expected['chp_year_one_electric_energy_produced_kwh'] = 4344703.75
        d_expected['chp_year_one_thermal_energy_produced_mmbtu'] = 9787.7
        d_expected['boiler_total_fuel_cost_us_dollars'] = 902.6
        d_expected['chp_total_fuel_cost_us_dollars'] = 4954813.24

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages'].get('error')))
            raise

