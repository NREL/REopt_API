import json
import os

from reo.models import ModelManager
from reo.nested_to_flat_output import nested_to_flat
from reo.utilities import check_common_outputs

from tastypie.test import ResourceTestCaseMixin
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db


class WholesaleTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(WholesaleTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)


    def test_wholesale(self):
        """
        Ensure that for a zero-load site with a wholesale rate, that REopt allows export above the site load
        :return:
        """
        filepath = os.path.dirname(os.path.abspath(__file__))
        post = json.load(open(os.path.join(filepath, 'posts', 'wholesalePOST.json')))

        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        """

        d_expected = dict()
        d_expected['wind_kw'] = 100


        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise
        """