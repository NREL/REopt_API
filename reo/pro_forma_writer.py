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

        self.year_one_bill = self.results.year_one_demand_cost + self.results.year_one_energy_cost
        self.year_one_bill_bau = self.results.year_one_demand_cost_bau + self.results.year_one_energy_cost_bau
        self.year_one_savings = self.year_one_bill_bau - self.year_one_bill

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
        ws['C61'] = self.year_one_bill_bau
        ws['C62'] = self.year_one_bill

        if self.econ.pv_macrs_schedule == 0:
            ws['B55'] = 0
            ws['B56'] = 0

        # Save
        wb.save(self.file_output)

    def compute_cashflow(self):

        n_cols = self.econ.analysis_period + 1

        # row_vectors
        value_of_savings = [0] * n_cols
        o_and_m_capacity_cost = [0] * n_cols
        batt_kw_replacement_cost = [0] * n_cols
        batt_kwh_replacement_cost = [0] * n_cols
        total_operating_expenses = [0] * n_cols

        # initialize values
        value_of_savings[1] = self.year_one_savings
        o_and_m_capacity_cost[1] = self.econ.pv_om

        inflation_modifier = 1 + self.econ.rate_inflation + self.econ.rate_escalation

        for year in range(1, n_cols):

            inflation_modifier_n = inflation_modifier ** year-1

            # Savings
            value_of_savings[year] = value_of_savings[year - 1] * inflation_modifier

            # Operating Expenses
            o_and_m_capacity_cost[year] = o_and_m_capacity_cost[year - 1] * inflation_modifier

            if self.self.econ.batt_replacement_year_kw == year:
                batt_kw_replacement_cost[year] = self.econ.batt_replacement_cost_kw * self.results.batt_kw * inflation_modifier_n









