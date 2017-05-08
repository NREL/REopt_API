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
        ws['B4'] = self.batt_kw
        ws['B5'] = self.batt_kwh
        ws['B9'] = self.capital_costs
        ws['B11'] = self.pv_om
        ws['B12'] = self.batt_replacement_cost_kw
        ws['B13'] = self.batt_replacement_year_kw
        ws['B14'] = self.batt_replacement_cost_kwh
        ws['B15'] = self.batt_replacement_year_kwh
        ws['B23'] = self.analysis_period
        ws['B24'] = self.rate_inflation * 100
        ws['B25'] = self.rate_escalation * 100
        ws['B26'] = self.owner_discount_rate * 100
        ws['B30'] = self.owner_tax_rate * 100
        ws['B41'] = self.pv_itc_federal * 100
        ws['C41'] = self.pv_itc_federal_max
        ws['B46'] = self.pv_itc_state
        ws['C46'] = self.pv_itc_state_max
        ws['B47'] = self.pv_itc_utility
        ws['C47'] = self.pv_itc_utility_max
        ws['B49'] = self.pv_rebate_federal
        ws['C49'] = self.pv_rebate_federal_max
        ws['B50'] = self.pv_rebate_state
        ws['C50'] = self.pv_rebate_state_max
        ws['B51'] = self.pv_rebate_utility
        ws['C51'] = self.pv_rebate_utility_max

        if self.pv_macrs == 0:
            ws['B54'] = 0
            ws['B55'] = 0

        # Save
        wb.save(self.file_output)
