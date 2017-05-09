import os
from openpyxl import load_workbook

class ProForma:

    file_template = "REoptCashFlowTemplate.xlsx"
    file_output = "ProForma.xlsx"

    def __init__(self, path_templates, path_output, econ, results):

        # paths
        self.file_template = os.path.join(path_templates, self.file_template)
        self.file_output = os.path.join(path_output, self.file_output)

        # data
        self.econ = econ
        self.results = results

        # input to template
        self.capital_costs = results.pv_kw * econ.pv_cost + \
                             results.batt_kw * econ.batt_cost_kw + \
                             results.batt_kwh * econ.batt_cost_kwh

        # ProForma outputs
        self.IRR = 0
        self.NPV = 0

    def update_template(self):

        sheet_io = "Inputs and Outputs"

        # Open file for reading
        wb = load_workbook(self.file_template)

        # Open Inputs Sheet
        ws = wb.get_sheet_by_name(sheet_io)

        # Modify inputs
        ws['B3'] = self.results.pv_kw
        ws['B4'] = self.econ.pv_degradation_rate * 100
        ws['B5'] = self.results.batt_kw
        ws['B6'] = self.results.batt_kwh
        ws['B7'] = self.results.average_yearly_pv_energy_produced / self.econ.pv_levelization_factor
        ws['B10'] = self.capital_costs
        ws['B12'] = self.econ.pv_om
        ws['B13'] = self.econ.batt_replacement_cost_kw
        ws['B14'] = self.econ.batt_replacement_year_kw
        ws['B15'] = self.econ.batt_replacement_cost_kwh
        ws['B16'] = self.econ.batt_replacement_year_kwh
        ws['B24'] = self.econ.analysis_period
        ws['B25'] = self.econ.rate_inflation * 100
        ws['B26'] = self.econ.rate_escalation * 100
        ws['B27'] = self.econ.owner_discount_rate * 100
        ws['B31'] = self.econ.owner_tax_rate * 100
        ws['B42'] = self.econ.pv_itc_federal * 100
        ws['C42'] = self.econ.pv_itc_federal_max
        ws['B47'] = self.econ.pv_itc_state * 100
        ws['C47'] = self.econ.pv_itc_state_max
        ws['B48'] = self.econ.pv_itc_utility * 100
        ws['C48'] = self.econ.pv_itc_utility_max
        ws['B50'] = self.econ.pv_rebate_federal
        ws['C50'] = self.econ.pv_rebate_federal_max
        ws['B51'] = self.econ.pv_rebate_state
        ws['C51'] = self.econ.pv_rebate_state_max
        ws['B52'] = self.econ.pv_rebate_utility
        ws['C52'] = self.econ.pv_rebate_utility_max
        ws['C61'] = self.results.year_one_demand_cost_bau + self.results.year_one_energy_cost_bau
        ws['C62'] = self.results.year_one_demand_cost + self.results.year_one_energy_cost

        if self.econ.pv_macrs_schedule == 0:
            ws['B55'] = 0
            ws['B56'] = 0

        # Save
        wb.save(self.file_output)
