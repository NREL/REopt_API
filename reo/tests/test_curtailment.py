# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
import json
import copy
import os
import pandas as pd
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat
from django.test import TestCase  
from reo.models import ModelManager
from reo.utilities import check_common_outputs
from reo.validators import ValidateNestedInput
from reo.src.wind import WindSAMSDK, combine_wind_files
import logging
logging.disable(logging.CRITICAL)


class WindTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(WindTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_curtailment(self):
        """
        Validation run for wind scenario with updated WindToolkit data
        Note no tax, no ITC, no MACRS.
        :return:
        """
        post_path = os.path.join('reo', 'tests', 'posts', 'test_curtailment_POST.json')
        with open(post_path, 'r') as fp:
            test_post = json.load(fp)
        d_expected = dict()
        d_expected['lcc'] = 5908025
        d_expected['npv'] = -4961719  # negative due to outage
        d_expected['average_annual_energy_curtailed_pv'] = 1180094
        d_expected['average_annual_energy_curtailed_wind'] = 2749637
        d_expected['total_pv_export'] = 0
        d_expected['total_wind_export'] = 0
        resp = self.get_response(data=test_post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        err_messages = d['messages'].get('error') or []
        if 'Wind Dataset Timed Out' in err_messages:
            print("Wind Dataset Timed Out")
        else:
            c = nested_to_flat(d['outputs'])
            c['average_annual_energy_curtailed_pv'] = sum(d['outputs']['Scenario']['Site']['PV'][
                                                              'year_one_curtailed_production_series_kw'])
            c['average_annual_energy_curtailed_wind'] = sum(d['outputs']['Scenario']['Site']['Wind'][
                                                                'year_one_curtailed_production_series_kw'])
            c['total_pv_export'] = sum(d['outputs']['Scenario']['Site']['PV']['year_one_to_grid_series_kw'])
            c['total_wind_export'] = sum(d['outputs']['Scenario']['Site']['Wind']['year_one_to_grid_series_kw'])
            try:
                check_common_outputs(self, c, d_expected)
            except:
                print("Run {} expected outputs may have changed.".format(run_uuid))
                print("Error message: {}".format(d['messages'].get('error')))
                raise
