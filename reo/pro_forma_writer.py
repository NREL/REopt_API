import os
from openpyxl import load_workbook

class ProForma:

    path_template = "templates"
    file_template = "REoptCashFlowTemplate.xlsx"
    file_output = "ProForma.xlsx"

    def __init__(self, path_output, economics, results):

        # paths
        self.file_template = os.path.join(self.path_templates, self.file_template)
        self.file_output = os.path.join(path_output, self.file_output)

        for k in economics.keys():
            setattr(self, k, economics.get(k))

        for k in results.keys():
            setattr(self, k, results.get(k))

        # inputs to template
        self.capital_costs = self.pv_kw * self.pv_cost + \
                             self.batt_kw * self.batt_cost_kw + \
                             self.batt_kwh * self.batt_cost_kwh

    def update_template(self):

        sheet_io = "Inputs and Outputs"

        # Open file for reading
        wb = load_workbook(self.file_template)

        # Open Inputs Sheet
        ws = wb.get_sheet_by_name(sheet_io)

        # Modify inputs
        ws['B3'] = self.pv_kw
        ws['B4'] = self.pv_degradation_rate
        ws['B5'] = self.batt_kw
        ws['B6'] = self.batt_kwh
        ws['B7'] = self.average_yearly_pv_energy_produced / self.pv_levelization_factor
        ws['B10'] = self.capital_costs
        ws['B12'] = self.pv_om
        ws['B13'] = self.batt_replacement_cost_kw
        ws['B14'] = self.batt_replacement_year_kw
        ws['B15'] = self.batt_replacement_cost_kwh
        ws['B16'] = self.batt_replacement_year_kwh
        ws['B24'] = self.analysis_period
        ws['B25'] = self.rate_inflation * 100
        ws['B26'] = self.rate_escalation * 100
        ws['B27'] = self.owner_discount_rate * 100
        ws['B31'] = self.owner_tax_rate * 100
        ws['B42'] = self.pv_itc_federal * 100
        ws['C42'] = self.pv_itc_federal_max
        ws['B47'] = self.pv_itc_state * 100
        ws['C47'] = self.pv_itc_state_max
        ws['B48'] = self.pv_itc_utility * 100
        ws['C48'] = self.pv_itc_utility_max
        ws['B50'] = self.pv_rebate_federal
        ws['C50'] = self.pv_rebate_federal_max
        ws['B51'] = self.pv_rebate_state
        ws['C51'] = self.pv_rebate_state_max
        ws['B52'] = self.pv_rebate_utility
        ws['C52'] = self.pv_rebate_utility_max
        ws['C61'] = self.year_one_demand_cost_bau + self.year_one_energy_cost_bau
        ws['C62'] = self.year_one_demand_cost + self.year_one_energy_cost

        if self.pv_macrs == 0:
            ws['B55'] = 0
            ws['B56'] = 0

        # Save
        wb.save(self.file_output)
