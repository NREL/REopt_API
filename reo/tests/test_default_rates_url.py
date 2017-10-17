from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.api_definitions import inputs

class DefaultsURLTest(ResourceTestCaseMixin, TestCase):

    def setUp(self):
    	self.default_value_url = '/reopt/default_api_inputs/'

	def test_default_api(self):
		response = self.api_client.get(self.default_value_url)
		expected_inputs = inputs(full_list=True)
		for k,v in json.loads(response.content).items():
			self.assertTrue(expected_inputs[k].get('default')==v)