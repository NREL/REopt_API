import json
import csv
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class EntryResourceTest(ResourceTestCaseMixin, TestCase):

	def setUp(self):
		super(EntryResourceTest, self).setUp()
		self.invalid_urdb_url = '/v1/invalid_urdb/'

	def test_problems(self):
		invalid_list = json.loads(self.api_client.get(self.invalid_urdb_url,format='json').content)['Invalid IDs']
		hard_problems = [i[0] for i in csv.reader(open('reo/hard_problems.csv','rb'))]
		for hp in hard_problems:
			self.assertTrue(hp in invalid_list)