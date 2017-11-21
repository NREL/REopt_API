from django.db import models
import uuid
import os
import datetime, tzlocal
from openpyxl import load_workbook
from reo.models import ScenarioModel
from reo.src.dat_file_manager import big_number


class ProForma(models.Model):

    scenariomodel = models.OneToOneField(
        ScenarioModel,
        on_delete=models.CASCADE,
        default=0,
        to_field='id',
        blank=True,
        primary_key=True
    )
    uuid = models.UUIDField(default=uuid.uuid4, null=False)
    spreadsheet_created = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    @classmethod
    def create(cls, scenariomodel, **kwargs ):
        pf = cls(scenariomodel = scenariomodel, **kwargs)

        file_dir = os.path.dirname(pf.output_file)
        
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        pf.save()        
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

        scenario = self.scenariomodel
        site = scenario.sitemodel_set.first()
        batt = site.storagemodel_set.first()
        pv = site.pvmodel_set.first()
        load_profile = site.loadprofilemodel_set.first()
        electric_tariff = site.electrictariffmodel_set.first()
        financial = site.financialmodel_set.first()

        # Open file for reading
        wb = load_workbook(self.file_template, read_only=False, keep_vba=True)

        # Open Inputs Sheet
        ws = wb.get_sheet_by_name(self.sheet_io)

        # handle None's
        pv_size_kw = pv.size_kw or 0
        batt_size_kw = batt.size_kw or 0
        batt_size_kwh = batt.size_kwh or 0

        pv_installed_cost_us_dollars_per_kw = pv.installed_cost_us_dollars_per_kw or 0
        batt_installed_cost_us_dollars_per_kw = batt.installed_cost_us_dollars_per_kw or 0
        batt_installed_cost_us_dollars_per_kwh = batt.installed_cost_us_dollars_per_kwh or 0
        pv_energy = pv.year_one_energy_produced_kwh or 0

        pv_cost = pv_size_kw * pv_installed_cost_us_dollars_per_kw
        batt_cost = batt_size_kw * batt_installed_cost_us_dollars_per_kw \
                    + batt_size_kwh * batt_installed_cost_us_dollars_per_kwh

        # System Design
        ws['B3'] = pv.size_kw or 0
        ws['B4'] = pv.degradation_pct * 100
        ws['B5'] = batt.size_kw or 0
        ws['B6'] = batt.size_kwh or 0

        # Year 1 Results
        ws['B9'] = electric_tariff.year_one_bill_bau_us_dollars or 0
        ws['B10'] = electric_tariff.year_one_bill_us_dollars or 0
        ws['B11'] = electric_tariff.year_one_export_benefit_us_dollars or 0
        ws['B12'] = pv_energy
        
        # System Costs
        ws['B15'] = pv_cost + batt_cost
        ws['B16'] = pv_cost
        ws['B17'] = batt_cost
        ws['B19'] = pv.om_cost_us_dollars_per_kw 
        ws['B20'] = batt.replace_cost_us_dollars_per_kw 
        ws['B21'] = batt.inverter_replacement_year 
        ws['B22'] = batt.replace_cost_us_dollars_per_kwh 
        ws['B23'] = batt.battery_replacement_year 

        # Analysis Parameters
        ws['B31'] = financial.analysis_years
        ws['B32'] = financial.om_cost_escalation_pct * 100
        ws['B33'] = financial.escalation_pct * 100
        ws['B34'] = financial.offtaker_discount_pct * 100 or 0

        # Tax rates
        ws['B37'] = financial.offtaker_tax_pct * 100 or 0

        # PV Tax Credits and Incentives
        ws['B42'] = pv.federal_itc_pct * 100
        ws['C42'] = ''
        ws['B47'] = pv.state_ibi_pct * 100
        ws['C47'] = pv.state_ibi_max_us_dollars
        ws['B48'] = pv.utility_ibi_pct * 100
        ws['C48'] = pv.utility_ibi_max_us_dollars
        ws['B50'] = pv.federal_rebate_us_dollars_per_kw * 0.001
        ws['C50'] = ''
        ws['B51'] = pv.state_rebate_us_dollars_per_kw * 0.001
        ws['C51'] = pv.state_rebate_max_us_dollars
        ws['B52'] = pv.utility_rebate_us_dollars_per_kw * 0.001
        ws['C52'] = pv.utility_rebate_max_us_dollars
        ws['B54'] = pv.pbi_us_dollars_per_kwh
        ws['C54'] = pv.pbi_max_us_dollars
        ws['E54'] = pv.pbi_years
        ws['F54'] = pv.pbi_system_max_kw

        # Battery Tax Credits and Incentives
        ws['B59'] = batt.total_itc_pct * 100
        ws['C59'] = big_number  # max itc
        ws['B64'] = 0  # state ITC
        ws['C64'] = big_number  # state ITC max
        ws['B65'] = 0  # utility ITC
        ws['C65'] = big_number  # utility ITC max
        ws['B67'] = batt.total_rebate_us_dollars_per_kw * 0.001
        ws['C67'] = big_number  # max rebate
        ws['B68'] = 0  # state rebate
        ws['C68'] = big_number  # max state rebate
        ws['B69'] = 0  # utility rebate
        ws['C69'] = big_number  # max utility rebate

        # Depreciation
        if pv.macrs_option_years > 0:
            ws['B72'] = pv.macrs_option_years
            ws['B73'] = pv.macrs_bonus_pct
        
        elif pv.macrs_option_years == 0:
            ws['B72'] = "None"
            ws['B73'] = 0

        if batt.macrs_option_years > 0:
            ws['C72'] = batt.macrs_option_years
            ws['C73'] = batt.macrs_bonus_pct
        
        elif batt.macrs_option_years == 0:
            ws['C72'] = "None"
            ws['C73'] = 0

        # Save
        wb.save(self.output_file)

        self.spreadsheet_created = tzlocal.get_localzone().localize(datetime.datetime.now())
        
        return True

