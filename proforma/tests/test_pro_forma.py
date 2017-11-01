from openpyxl import load_workbook
import tzlocal
import json
import datetime
import os
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from django.test import Client
from proforma.models import ProForma


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
        uuid = run_output['outputs']['Scenario']['run_uuid']
       

        start_time = now()
        response = Client().get('/proforma/?run_uuid='+uuid)
        self.assertEqual(response.status_code,200)

        pf = ProForma.objects.get(scenario_model=uuid)

        self.assertTrue(os.path.exists(pf.output_file))
        self.assertTrue(pf.spreadsheet_created < now() and pf.spreadsheet_created > start_time)

        wb = load_workbook(pf.output_file, read_only=False, keep_vba=True)
        ws = wb.get_sheet_by_name(pf.sheet_io)
        
        ro = REoptResponse.objects.get(pk=id)
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
        [ws['B32'],ro.om_cost_growth_rate * 100],
        [ws['B33'],ro.rate_escalation * 100],
        [ws['B34'],ro.owner_discount_rate * 100],
        [ws['B37'],ro.owner_tax_rate * 100],
        [ws['B42'],ro.pv_itc_federal * 100],
        [ws['C42'],ro.pv_itc_federal_max],
        [ws['B47'],ro.pv_ibi_state * 100],
        [ws['C47'],ro.pv_ibi_state_max],
        [ws['B48'],ro.pv_ibi_utility * 100],
        [ws['C48'],ro.pv_ibi_utility_max],
        [ws['B50'],ro.pv_rebate_federal * 0.001],
        [ws['C50'],ro.pv_rebate_federal_max],
        [ws['B51'],ro.pv_rebate_state * 0.001],
        [ws['C51'],ro.pv_rebate_state_max],
        [ws['B52'],ro.pv_rebate_utility * 0.001],
        [ws['C52'],ro.pv_rebate_utility_max],
        [ws['B54'],ro.pv_pbi],
        [ws['C54'],ro.pv_pbi_max],
        [ws['E54'],ro.pv_pbi_years],
        [ws['F54'],ro.pv_pbi_system_max],
        [ws['B59'],ro.batt_itc_total * 100],
        [ws['B67'],ro.batt_rebate_total],
        [ws['B72'],ro.pv_macrs_schedule],
        [ws['B73'],ro.pv_macrs_bonus_fraction],
        [ws['C72'],ro.batt_macrs_schedule],
        [ws['C73'],ro.batt_macrs_bonus_fraction]]

        [self.assertAlmostEqual(float(a.value), b, places=2) for a,b in mapping]
