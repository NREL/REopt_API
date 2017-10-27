from django.db import models
import uuid
import os
import datetime, tzlocal
from openpyxl import load_workbook
from reo.models import REoptResponse
from reo.src.dat_file_manager import big_number


class ProForma(models.Model):

    run_output = models.ForeignKey(REoptResponse)
    uuid = models.UUIDField(default=uuid.uuid4, null=False)
    spreadsheet_created = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    @classmethod
    def create(cls, **kwargs):
        pf = cls(**kwargs)

        file_dir = os.path.dirname(pf.output_file)
        
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)

        pf.generate_spreadsheet()
        
        return pf
    
    @property
    def sheet_io(self):
        return "Inputs and Outputs"

    @property
    def file_template(self):
        return os.path.join('proforma',"REoptCashFlowTemplate.xlsm")

    @property
    def output_file_name(self):
        return "ProForma.xlsm"

    @property
    def output_file(self):
        return os.path.join(os.getcwd(),'static', 'files', str(self.uuid), self.output_file_name)
          
    def generate_spreadsheet(self):

        ro = self.run_output

        # Open file for reading
        wb = load_workbook(self.file_template, read_only=False, keep_vba=True)

        # Open Inputs Sheet
        ws = wb.get_sheet_by_name(self.sheet_io)

        # System Design
        ws['B3'] = ro.pv_kw
        ws['B4'] = ro.pv_degradation_rate * 100
        ws['B5'] = ro.batt_kw
        ws['B6'] = ro.batt_kwh

        # Year 1 Results
        ws['B9'] = ro.year_one_bill_bau
        ws['B10'] = ro.year_one_bill
        ws['B11'] = ro.year_one_export_benefit
        ws['B12'] = ro.year_one_energy_produced

        # System Costs
        ws['B15'] = ro.total_capital_costs
        ws['B16'] = ro.pv_installed_cost
        ws['B17'] = ro.battery_installed_cost
        ws['B19'] = ro.pv_om
        ws['B20'] = ro.batt_replacement_cost_kw
        ws['B21'] = ro.batt_replacement_year_kw
        ws['B22'] = ro.batt_replacement_cost_kwh
        ws['B23'] = ro.batt_replacement_year_kwh

        # Analysis Parameters
        ws['B31'] = ro.analysis_period
        ws['B32'] = ro.om_cost_growth_rate * 100
        ws['B33'] = ro.rate_escalation * 100
        ws['B34'] = ro.owner_discount_rate * 100

        # Tax rates
        ws['B37'] = ro.owner_tax_rate * 100

        # PV Tax Credits and Incentives
        ws['B42'] = ro.pv_itc_federal * 100
        ws['C42'] = ro.pv_itc_federal_max
        ws['B47'] = ro.pv_ibi_state * 100
        ws['C47'] = ro.pv_ibi_state_max
        ws['B48'] = ro.pv_ibi_utility * 100
        ws['C48'] = ro.pv_ibi_utility_max
        ws['B50'] = ro.pv_rebate_federal * 0.001
        ws['C50'] = ro.pv_rebate_federal_max
        ws['B51'] = ro.pv_rebate_state * 0.001
        ws['C51'] = ro.pv_rebate_state_max
        ws['B52'] = ro.pv_rebate_utility * 0.001
        ws['C52'] = ro.pv_rebate_utility_max
        ws['B54'] = ro.pv_pbi
        ws['C54'] = ro.pv_pbi_max
        ws['E54'] = ro.pv_pbi_years
        ws['F54'] = ro.pv_pbi_system_max

        # Battery Tax Credits and Incentives
        ws['B59'] = ro.batt_itc_total * 100
        ws['C59'] = big_number  # max itc
        ws['B64'] = 0  # state ITC
        ws['C64'] = big_number  # state ITC max
        ws['B65'] = 0  # utility ITC
        ws['C65'] = big_number  # utility ITC max
        ws['B67'] = ro.batt_rebate_total * 0.001
        ws['C67'] = big_number  # max rebate
        ws['B68'] = 0  # state rebate
        ws['C68'] = big_number  # max state rebate
        ws['B69'] = 0  # utility rebate
        ws['C69'] = big_number  # max utility rebate

        # Depreciation
        if ro.pv_macrs_schedule > 0:
            ws['B72'] = ro.pv_macrs_schedule
            ws['B73'] = ro.pv_macrs_bonus_fraction
        elif ro.pv_macrs_schedule == 0:
            ws['B72'] = "None"
            ws['B73'] = 0

        if ro.batt_macrs_schedule > 0:
            ws['C72'] = ro.batt_macrs_schedule
            ws['C73'] = ro.batt_macrs_bonus_fraction
        if ro.batt_macrs_schedule == 0:
            ws['C72'] = "None"
            ws['C73'] = 0

        # Save
        wb.save(self.output_file)

        self.spreadsheet_created = tzlocal.get_localzone().localize(datetime.datetime.now())
        
        return True

