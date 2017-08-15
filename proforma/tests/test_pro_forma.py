from openpyxl import load_workbook
import tzlocal
import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.validators import *
from reo.models import RunOutput
from django.test import Client
from proforma.models import ProForma
import datetime


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
        uuid = run_output['uuid']
        id = run_output['id']

        start_time = now()
        response = Client().get('/proforma/?run_uuid='+uuid)
        self.assertEqual(response.status_code,200)

        pf = ProForma.objects.get(run_output_id=id)

        self.assertTrue(os.path.exists(pf.output_file))
        self.assertTrue(pf.spreadsheet_created < now() and pf.spreadsheet_created > start_time)

        wb = load_workbook(pf.output_file, read_only=False, keep_vba=True)
        ws = wb.get_sheet_by_name(pf.sheet_io)
        
        ro = RunOutput.objects.get(pk=id)
        mapping = [[ws['B3'],ro.pv_kw],
        [ws['B4'],ro.pv_degradation_rate * 100],
        [ws['B5'],ro.batt_kw],
        [ws['B6'],ro.batt_kwh],
        [ws['B9'],ro.year_one_bill_bau],
        [ws['B10'],ro.year_one_bill],
        [ws['B11'],ro.year_one_export_benefit],
        [ws['B12'],ro.year_one_energy_produced],
        [ws['B15'],ro.total_capital_costs],
        [ws['B16'],ro.pv_installed_cost],
        [ws['B17'],ro.battery_installed_cost],
        [ws['B19'],ro.pv_om],
        [ws['B20'],ro.batt_replacement_cost_kw],
        [ws['B21'],ro.batt_replacement_year_kw],
        [ws['B22'],ro.batt_replacement_cost_kwh],
        [ws['B23'],ro.batt_replacement_year_kwh],
        [ws['B31'],ro.analysis_period],
        [ws['B32'],ro.rate_inflation * 100],
        [ws['B33'],ro.rate_escalation * 100],
        [ws['B35'],ro.owner_discount_rate * 100],
        [ws['B39'],ro.owner_tax_rate * 100],
        [ws['B44'],ro.pv_itc_federal * 100],
        [ws['C44'],ro.pv_itc_federal_max],
        [ws['B49'],ro.pv_itc_state * 100],
        [ws['C49'],ro.pv_itc_state_max],
        [ws['B50'],ro.pv_itc_utility * 100],
        [ws['C50'],ro.pv_itc_utility_max],
        [ws['B52'],ro.pv_rebate_federal * 0.001],
        [ws['C52'],ro.pv_rebate_federal_max],
        [ws['B53'],ro.pv_rebate_state * 0.001],
        [ws['C53'],ro.pv_rebate_state_max],
        [ws['B54'],ro.pv_rebate_utility * 0.001],
        [ws['C54'],ro.pv_rebate_utility_max],
        [ws['B56'],ro.pv_pbi],
        [ws['C56'],ro.pv_pbi_max],
        [ws['E56'],ro.pv_pbi_years],
        [ws['F56'],ro.pv_pbi_system_max],
        [ws['B61'],ro.batt_itc_federal * 100],
        [ws['C61'],ro.batt_itc_federal_max],
        [ws['B66'],ro.batt_itc_state * 100],
        [ws['C66'],ro.batt_itc_state_max],
        [ws['B67'],ro.batt_itc_utility * 100],
        [ws['C67'],ro.batt_itc_utility_max],
        [ws['B69'],ro.batt_rebate_federal],
        [ws['C69'],ro.batt_rebate_federal_max],
        [ws['B70'],ro.batt_rebate_state],
        [ws['C70'],ro.batt_rebate_state_max],
        [ws['B71'],ro.batt_rebate_utility],
        [ws['C71'],ro.batt_rebate_utility_max],
        [ws['B74'],ro.pv_macrs_schedule],
        [ws['B75'],ro.pv_macrs_bonus_fraction],
        [ws['C74'],ro.batt_macrs_schedule],
        [ws['C75'],ro.batt_macrs_bonus_fraction]]

        [self.assertAlmostEqual(a.value, b, places = 2) for a,b in mapping]
 	
