from openpyxl import load_workbook
import tzlocal
import json
import datetime
import os
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from django.test import Client
from proforma.models import ProForma
from reo.models import ScenarioModel

def now():
    return tzlocal.get_localzone().localize(datetime.datetime.now())


class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    REopt_tol = 5e-5

    def setUp(self):
        super(EntryResourceTest, self).setUp()

        self.example_reopt_request_data = json.loads(open('proforma/tests/test_data.json').read())
        
        self.url_base = '/api/v1/reopt/'

    def get_response(self, data):
        return self.api_client.post(self.url_base, format='json', data=data)

    def test_creation(self):
        run_output = json.loads(self.get_response(self.example_reopt_request_data).content)
        uuid = run_output['outputs']['run_uuid']
       
        start_time = now()
        response = Client().get('/proforma/?run_uuid='+uuid)
        self.assertEqual(response.status_code,200)

        scenario = ScenarioModel.objects.get(run_uuid=uuid)
        pf = ProForma.objects.get(scenariomodel=scenario)
        self.assertTrue(os.path.exists(pf.output_file))
        self.assertTrue(pf.spreadsheet_created < now() and pf.spreadsheet_created > start_time)

        wb = load_workbook(pf.output_file, read_only=False, keep_vba=True)
        ws = wb.get_sheet_by_name(pf.sheet_io)
        
        mapping = [[ws['B3'],0.889873],
        [ws['B4'],0.5],
        [ws['B5'],0],
        [ws['B6'],0],
        [ws['B9'],11649.69],
        [ws['B10'],11527.08],
        [ws['B11'],0],
        [ws['B12'],1642],
        [ws['B15'],863],
        [ws['B16'],1779.746],
        [ws['B17'],0],
        [ws['B19'],16],
        [ws['B20'],460],
        [ws['B21'],10],
        [ws['B22'],230],
        [ws['B23'],10],
        [ws['B31'],20],
        [ws['B32'],2.5],
        [ws['B33'],2.6],
        [ws['B34'],0],
        [ws['B37'],0],
        [ws['B42'],30],
       # [ws['C42'],''],
        [ws['B47'],0],
        [ws['C47'],10000000000],
        [ws['B48'],0],
        [ws['C48'],10000000000],
        [ws['B50'],0],
       # [ws['C50'],''],
        [ws['B51'],0],
        [ws['C51'],10000000000],
        [ws['B52'],0],
        [ws['C52'],10000000000],
        [ws['B54'],0],
        [ws['C54'],1000000000],
        [ws['E54'],1],
        [ws['F54'],1000000000],
        [ws['B59'],0],
        [ws['B67'],0],
        [ws['B72'],5],
        [ws['B73'],0.5],
        [ws['C72'],5],
        [ws['C73'],0.5]]

        [self.assertAlmostEqual(float(a.value), b, places=2) for a,b in mapping]
