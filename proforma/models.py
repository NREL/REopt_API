from django.db import models
import uuid
import os
import datetime, tzlocal
from openpyxl import load_workbook
from reo.models import ScenarioModel, SiteModel, PVModel, WindModel, StorageModel, FinancialModel, ElectricTariffModel, LoadProfileModel
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
        batt = StorageModel.objects.filter(run_uuid=scenario.run_uuid).first()
        pv = PVModel.objects.filter(run_uuid=scenario.run_uuid).first()
        wind = WindModel.objects.filter(run_uuid=scenario.run_uuid).first()
        electric_tariff = ElectricTariffModel.objects.filter(run_uuid=scenario.run_uuid).first()
        financial = FinancialModel.objects.filter(run_uuid=scenario.run_uuid).first()

        # Open file for reading
        wb = load_workbook(self.file_template, read_only=False, keep_vba=True)

        # Open Inputs Sheet
        ws = wb.get_sheet_by_name(self.sheet_io)

        # handle None's
        pv_installed_kw = pv.size_kw or 0
        if pv_installed_kw > 0 and pv.existing_kw > 0:
            pv_installed_kw -= pv.existing_kw
        batt_size_kw = batt.size_kw or 0
        batt_size_kwh = batt.size_kwh or 0
        wind_installed_kw = wind.size_kw or 0

        pv_installed_cost_us_dollars_per_kw = pv.installed_cost_us_dollars_per_kw or 0
        batt_installed_cost_us_dollars_per_kw = batt.installed_cost_us_dollars_per_kw or 0
        batt_installed_cost_us_dollars_per_kwh = batt.installed_cost_us_dollars_per_kwh or 0
        wind_installed_cost_us_dollars_per_kw = wind.installed_cost_us_dollars_per_kw or 0
        pv_energy = pv.year_one_energy_produced_kwh or 0
        wind_energy = wind.year_one_energy_produced_kwh or 0

        pv_cost = pv_installed_kw * pv_installed_cost_us_dollars_per_kw
        batt_cost = batt_size_kw * batt_installed_cost_us_dollars_per_kw \
                    + batt_size_kwh * batt_installed_cost_us_dollars_per_kwh
        wind_cost = wind_installed_kw * wind_installed_cost_us_dollars_per_kw

        # System Design
        ws['B3'] = pv_installed_kw
        ws['B4'] = pv.existing_kw or 0
        ws['B5'] = pv.degradation_pct * 100
        ws['B6'] = wind_installed_kw
        ws['B7'] = batt.size_kw or 0
        ws['B8'] = batt.size_kwh or 0

        # Year 1 Results
        ws['B11'] = electric_tariff.year_one_bill_bau_us_dollars or 0
        ws['B12'] = electric_tariff.year_one_bill_us_dollars or 0
        ws['B13'] = electric_tariff.year_one_export_benefit_us_dollars or 0
        ws['B14'] = pv_energy
        ws['B15'] = wind_energy
        ws['B16'] = wind_energy + pv_energy

        # System Costs
        ws['B19'] = pv_cost + batt_cost + wind_cost
        ws['B20'] = pv_cost
        ws['B21'] = wind_cost
        ws['B22'] = batt_cost
        ws['B24'] = pv.om_cost_us_dollars_per_kw
        ws['B25'] = wind.om_cost_us_dollars_per_kw
        ws['B26'] = batt.replace_cost_us_dollars_per_kw
        ws['B27'] = batt.inverter_replacement_year
        ws['B28'] = batt.replace_cost_us_dollars_per_kwh
        ws['B29'] = batt.battery_replacement_year

        # Analysis Parameters
        ws['B37'] = financial.analysis_years
        ws['B38'] = financial.om_cost_escalation_pct * 100
        ws['B39'] = financial.escalation_pct * 100
        ws['B40'] = financial.offtaker_discount_pct * 100

        # Tax rates
        ws['B43'] = financial.offtaker_tax_pct * 100

        # PV Tax Credits and Incentives
        ws['B48'] = pv.federal_itc_pct * 100
        ws['C48'] = ''
        ws['B53'] = pv.state_ibi_pct * 100
        ws['C53'] = pv.state_ibi_max_us_dollars
        ws['B54'] = pv.utility_ibi_pct * 100
        ws['C54'] = pv.utility_ibi_max_us_dollars
        ws['B56'] = pv.federal_rebate_us_dollars_per_kw * 0.001
        ws['C56'] = ''
        ws['B57'] = pv.state_rebate_us_dollars_per_kw * 0.001
        ws['C57'] = pv.state_rebate_max_us_dollars
        ws['B58'] = pv.utility_rebate_us_dollars_per_kw * 0.001
        ws['C58'] = pv.utility_rebate_max_us_dollars
        ws['B60'] = pv.pbi_us_dollars_per_kwh
        ws['C60'] = pv.pbi_max_us_dollars
        ws['E60'] = pv.pbi_years
        ws['F60'] = pv.pbi_system_max_kw

        # Wind Tax Credits and Incentives
        ws['B65'] = wind.federal_itc_pct * 100
        ws['C65'] = ''
        ws['B70'] = wind.state_ibi_pct * 100
        ws['C70'] = wind.state_ibi_max_us_dollars
        ws['B71'] = wind.utility_ibi_pct * 100
        ws['C71'] = wind.utility_ibi_max_us_dollars
        ws['B73'] = wind.federal_rebate_us_dollars_per_kw * 0.001
        ws['C73'] = ''
        ws['B74'] = wind.state_rebate_us_dollars_per_kw * 0.001
        ws['C74'] = wind.state_rebate_max_us_dollars
        ws['B75'] = wind.utility_rebate_us_dollars_per_kw * 0.001
        ws['C75'] = wind.utility_rebate_max_us_dollars
        ws['B77'] = wind.pbi_us_dollars_per_kwh
        ws['C77'] = wind.pbi_max_us_dollars
        ws['E77'] = wind.pbi_years
        ws['F77'] = wind.pbi_system_max_kw

        # Battery Tax Credits and Incentives
        ws['B82'] = batt.total_itc_pct * 100
        ws['C82'] = big_number  # max itc
        ws['B87'] = 0  # state ITC
        ws['C87'] = big_number  # state ITC max
        ws['B88'] = 0  # utility ITC
        ws['C88'] = big_number  # utility ITC max
        ws['B90'] = batt.total_rebate_us_dollars_per_kw * 0.001
        ws['C90'] = big_number  # max rebate
        ws['B91'] = 0  # state rebate
        ws['C91'] = big_number  # max state rebate
        ws['B92'] = 0  # utility rebate
        ws['C92'] = big_number  # max utility rebate

        # Depreciation
        if pv.macrs_option_years > 0:
            ws['B95'] = pv.macrs_option_years
            ws['B96'] = pv.macrs_bonus_pct
        
        elif pv.macrs_option_years == 0:
            ws['B95'] = "None"
            ws['B96'] = 0

        if batt.macrs_option_years > 0:
            ws['C95'] = batt.macrs_option_years
            ws['C96'] = batt.macrs_bonus_pct
        
        elif batt.macrs_option_years == 0:
            ws['C95'] = "None"
            ws['C96'] = 0

        if wind.macrs_option_years > 0:
            ws['D95'] = wind.macrs_option_years
            ws['D96'] = wind.macrs_bonus_pct

        elif wind.macrs_option_years == 0:
            ws['D95'] = "None"
            ws['D96'] = 0

        # Save
        wb.save(self.output_file)

        self.spreadsheet_created = tzlocal.get_localzone().localize(datetime.datetime.now())
        
        return True

