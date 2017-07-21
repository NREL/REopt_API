
import json
import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.api_definitions import *
from reo.validators import *
import numpy as np
from reo.models import RunOutput
from proforma.models import ProForma



class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    REopt_tol = 5e-5

    def setUp(self):
        super(EntryResourceTest, self).setUp()

        self.example_reopt_request_data = json.loads(open('proforma/tests/test_data.json').read())
        
        self.url_base = '/api/v1/reopt/'

    def get_response(self, data):
        return self.api_client.post(self.url_base, format='json', data=data)

    def test_file_created(self):
        from IPython import embed
        embed()
        uuid =  self.get_response(self.example_reopt_request_data)


