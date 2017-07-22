from django.db import models
import uuid
import os
import math
import datetime, tzlocal
import numpy as np
from openpyxl import load_workbook
from reo.economics import Economics
from reo.models import RunOutput

# logging
from log_levels import log


class ProForma(models.Model):

    run_output = models.ForeignKey(RunOutput) 
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
        ws['B32'] = ro.rate_inflation * 100
        ws['B33'] = ro.rate_escalation * 100
        ws['B35'] = ro.owner_discount_rate * 100

        # Tax rates
        ws['B39'] = ro.owner_tax_rate * 100

        # PV Tax Credits and Incentives
        ws['B44'] = ro.pv_itc_federal * 100
        ws['C44'] = ro.pv_itc_federal_max
        ws['B49'] = ro.pv_itc_state * 100
        ws['C49'] = ro.pv_itc_state_max
        ws['B50'] = ro.pv_itc_utility * 100
        ws['C50'] = ro.pv_itc_utility_max
        ws['B52'] = ro.pv_rebate_federal * 0.001
        ws['C52'] = ro.pv_rebate_federal_max
        ws['B53'] = ro.pv_rebate_state * 0.001
        ws['C53'] = ro.pv_rebate_state_max
        ws['B54'] = ro.pv_rebate_utility * 0.001
        ws['C54'] = ro.pv_rebate_utility_max
        ws['B56'] = ro.pv_pbi
        ws['C56'] = ro.pv_pbi_max
        ws['E56'] = ro.pv_pbi_years
        ws['F56'] = ro.pv_pbi_system_max

        # Battery Tax Credits and Incentives
        ws['B61'] = ro.batt_itc_federal * 100
        ws['C61'] = ro.batt_itc_federal_max
        ws['B66'] = ro.batt_itc_state * 100
        ws['C66'] = ro.batt_itc_state_max
        ws['B67'] = ro.batt_itc_utility * 100
        ws['C67'] = ro.batt_itc_utility_max
        ws['B69'] = ro.batt_rebate_federal
        ws['C69'] = ro.batt_rebate_federal_max
        ws['B70'] = ro.batt_rebate_state
        ws['C70'] = ro.batt_rebate_state_max
        ws['B71'] = ro.batt_rebate_utility
        ws['C71'] = ro.batt_rebate_utility_max

        # Depreciation
        if ro.pv_macrs_schedule > 0:
            ws['B74'] = ro.pv_macrs_schedule
            ws['B75'] = ro.pv_macrs_bonus_fraction
        
        if ro.batt_macrs_schedule > 0:
            ws['C74'] = ro.batt_macrs_schedule
            ws['C75'] = ro.batt_macrs_bonus_fraction

        # Save
        wb.save(self.output_file)

        self.spreadsheet_created = tzlocal.get_localzone().localize(datetime.datetime.now())
        
        return True

