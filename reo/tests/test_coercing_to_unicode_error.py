import time
import json
import os
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from reo.models import ModelManager
from reo.utilities import check_common_outputs


class UnicodeErrorTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(UnicodeErrorTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_where_is_coercing_to_unicode_error_happening(self):
        """
        Using https://github.nrel.gov/raw/gist/nmuerdte/6b46ecfb0abff68f6bbebfd1388b1d41/raw/3b504c3ae01045d496048e34c9e32d73122ea3a3/coercing-to-unicode-error.json hyperlink to reproduce the error
        :return:
        """
        test_post = os.path.join('reo', 'tests', 'posts', 'unicodeErrorPOST.json')
        nested_data = json.load(open(test_post, 'rb'))
        # comment out  the following line if want to reproduce the error
        nested_data['Scenario']['Site']['LoadProfile']['doe_reference_name'] = 'MediumOffice'
        #nested_data['Scenario']['Site']['LoadProfile']['outage_is_major_event'] = False
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')        
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])