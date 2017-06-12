import os
import math
import numpy as np
from openpyxl import load_workbook

# logging
from log_levels import log

class ProForma(object):

    file_template = "REoptCashFlowTemplate.xlsm"
    file_output = "ProForma.xlsm"

    def __init__(self, path_templates, path_output, econ, results):

        # paths
        self.file_template = os.path.join(path_templates, self.file_template)
        self.file_output = os.path.join(path_output, self.file_output)

        # data
        self.econ = econ
        self.results = results

        # system sizes
        self.pv_kw = results.pv_kw
        self.batt_kw = results.batt_kw
        self.batt_kwh = results.batt_kwh

        if self.pv_kw is None:
            self.pv_kw = 0
        if self.batt_kw is None:
            self.batt_kw = 0
        if self.batt_kwh is None:
            self.batt_kwh = 0

        # input to template
        self.capital_costs = self.pv_kw * econ.pv_cost + \
                             self.batt_kw * econ.batt_cost_kw + \
                             self.batt_kwh * econ.batt_cost_kwh

        self.year_one_bill = self.results.year_one_demand_cost + self.results.year_one_energy_cost
        self.year_one_exports = self.results.year_one_export_benefit
        self.year_one_bill_bau = self.results.year_one_demand_cost_bau + self.results.year_one_energy_cost_bau
        self.year_one_savings = self.year_one_bill_bau - self.year_one_bill

        # no state taxes for now
        self.state_tax_owner = 0
        self.fed_tax_owner = self.econ.owner_tax_rate

        # Unit test outputs
        self.state_depr_basis_calc = 0
        self.state_itc_basis_calc = 0
        self.fed_depr_basis_calc = 0
        self.fed_itc_basis_calc = 0
        self.state_tax_liability = list()
        self.federal_tax_liability = list()
        self.bill_with_sys = list()
        self.bill_bau = list()
        self.exports_with_sys = list()
        self.total_operating_expenses = list()
        self.after_tax_annual_costs = list()
        self.after_tax_value = list()
        self.after_tax_cash_flow = list()
        self.net_annual_cost_without_sys = list()
        self.net_annual_cost_with_sys = list()

        # ProForma outputs
        self.irr = 0
        self.npv = 0
        self.lcc = 0
        self.lcc_bau = 0

        # tax credits
        self.itc_fed_percent = self.econ.pv_itc_federal
        self.itc_fed_percent_maxvalue = self.econ.pv_itc_federal_max

        # cash incentives (need to rename state, util from ITC)
        self.ibi_sta_percent = self.econ.pv_itc_state
        self.ibi_sta_percent_maxvalue = self.econ.pv_itc_state_max
        self.ibi_uti_percent = self.econ.pv_itc_utility
        self.ibi_uti_percent_maxvalue = self.econ.pv_itc_utility_max

        # capacity based incentives
        self.cbi_fed_amount = self.econ.pv_rebate_federal
        self.cbi_fed_maxvalue = self.econ.pv_rebate_federal_max
        self.cbi_sta_amount = self.econ.pv_rebate_state
        self.cbi_sta_maxvalue = self.econ.pv_rebate_state_max
        self.cbi_uti_amount = self.econ.pv_rebate_utility
        self.cbi_uti_maxvalue = self.econ.pv_rebate_utility_max

        # production based incentives
        self.pbi_combined_amount = self.econ.pv_pbi
        self.pbi_combined_maxvalue = self.econ.pv_pbi_max
        self.pbi_combined_term = self.econ.pv_pbi_years

        # tax credits reduce depreciation and ITC basis
        self.itc_fed_percent_deprbas_fed = True
        self.itc_fed_percent_deprbas_sta = True

        # cash incentive is taxable
        self.ibi_sta_percent_tax_fed = True
        self.ibi_sta_percent_tax_sta = True
        self.ibi_uti_percent_tax_fed = True
        self.ibi_uti_percent_tax_sta = True

        self.cbi_fed_tax_fed = True
        self.cbi_fed_tax_sta = True
        self.cbi_sta_tax_fed = True
        self.cbi_sta_tax_sta = True
        self.cbi_uti_tax_fed = True
        self.cbi_uti_tax_sta = True

        self.pbi_combined_tax_fed = True
        self.pbi_combined_tax_sta = True

        # incentive reduces depreciation and ITC basis
        self.ibi_sta_percent_deprbas_fed = False
        self.ibi_sta_percent_deprbas_sta = False
        self.ibi_uti_percent_deprbas_fed = False
        self.ibi_uti_percent_deprbas_sta = False

        self.cbi_fed_deprbas_fed = False
        self.cbi_fed_deprbas_sta = False
        self.cbi_sta_deprbas_fed = False
        self.cbi_sta_deprbas_sta = False
        self.cbi_uti_deprbas_fed = False
        self.cbi_uti_deprbas_sta = False

        # Assume state MACRS the same as fed
        self.state_depreciation_equals_federal = True

    def get_irr(self):
        return self.irr

    def get_npv(self):
        return round(self.npv)

    def get_lcc(self):
        return round(self.lcc)

    def get_lcc_bau(self):
        return round(self.lcc_bau)

    def update_template(self):

        sheet_io = "Inputs and Outputs"

        # Open file for reading
        wb = load_workbook(self.file_template, read_only=False, keep_vba=True)

        # Open Inputs Sheet
        ws = wb.get_sheet_by_name(sheet_io)

        # Modify inputs
        ws['B3'] = self.pv_kw
        ws['B4'] = self.econ.pv_degradation_rate * 100
        ws['B5'] = self.batt_kw
        ws['B6'] = self.batt_kwh
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
        ws['B31'] = self.fed_tax_owner * 100
        ws['B36'] = self.econ.pv_itc_federal * 100
        ws['C36'] = self.econ.pv_itc_federal_max
        ws['B41'] = self.econ.pv_itc_state * 100
        ws['C41'] = self.econ.pv_itc_state_max
        ws['B42'] = self.econ.pv_itc_utility * 100
        ws['C42'] = self.econ.pv_itc_utility_max
        ws['B44'] = self.econ.pv_rebate_federal
        ws['C44'] = self.econ.pv_rebate_federal_max
        ws['B45'] = self.econ.pv_rebate_state
        ws['C45'] = self.econ.pv_rebate_state_max
        ws['B46'] = self.econ.pv_rebate_utility
        ws['C46'] = self.econ.pv_rebate_utility_max
        ws['B53'] = self.econ.pv_macrs_bonus_fraction
        ws['C56'] = self.year_one_bill_bau
        ws['C57'] = self.year_one_bill
        ws['C58'] = self.year_one_exports

        if self.econ.pv_macrs_schedule == 0:
            ws['B51'] = 0

        # Save
        wb.save(self.file_output)

    def compute_cashflow(self):

        n_cols = self.econ.analysis_period + 1

        # row_vectors to match template spreadsheet
        zero_list = [0] * n_cols
        annual_energy = list(zero_list)
        bill_without_system = list(zero_list)
        bill_with_system = list(zero_list)
        exports_with_system = list(zero_list)
        value_of_savings = list(zero_list)
        o_and_m_capacity_cost = list(zero_list)
        batt_kw_replacement_cost = list(zero_list)
        batt_kwh_replacement_cost = list(zero_list)
        total_operating_expenses = list(zero_list)
        total_deductible_expenses = list(zero_list)
        debt_amount = list(zero_list)
        pre_tax_cash_flow = list(zero_list)
        total_investment_based_incentives = list(zero_list)
        total_capacity_based_incentives = list(zero_list)
        total_production_based_incentives = list(zero_list)
        federal_taxable_income_before_deductions = list(zero_list)
        federal_depreciation_amount = list(zero_list)
        federal_total_deductions = list(zero_list)
        federal_income_tax = list(zero_list)
        federal_tax_liability = list(zero_list)
        after_tax_annual_costs = list(zero_list)
        after_tax_value_of_energy = list(zero_list)
        after_tax_cash_flow = list(zero_list)
        net_annual_costs_with_system = list(zero_list)
        net_annual_costs_without_system = list(zero_list)

        # incentives, tax credits, depreciation
        federal_itc = min(self.itc_fed_percent * self.capital_costs, self.itc_fed_percent_maxvalue)
        state_ibi = min(self.ibi_sta_percent * self.capital_costs, self.ibi_sta_percent_maxvalue)
        utility_ibi = min(self.ibi_uti_percent * self.capital_costs, self.ibi_uti_percent_maxvalue)
        federal_cbi = min(self.cbi_fed_amount * self.pv_kw, self.cbi_fed_maxvalue)
        state_cbi = min(self.cbi_sta_amount * self.pv_kw, self.cbi_sta_maxvalue)
        utility_cbi = min(self.cbi_uti_amount * self.pv_kw, self.cbi_uti_maxvalue)

        federal_itc_basis = self.federal_itc_basis(state_ibi, utility_ibi, federal_cbi, state_cbi, utility_cbi)
        federal_depreciation_basis = self.federal_depreciation_basis(federal_itc, state_ibi, utility_ibi, federal_cbi,
                                                                     state_cbi, utility_cbi)
        macrs_schedule = self.econ.pv_macrs_schedule_array

        # year 0 initializations
        debt_amount[0] = self.capital_costs
        pre_tax_cash_flow[0] = -debt_amount[0]
        total_investment_based_incentives[0] = state_ibi + utility_ibi
        total_capacity_based_incentives[0] = federal_cbi + state_cbi + utility_cbi
        after_tax_annual_costs[0] = total_investment_based_incentives[0] + total_capacity_based_incentives[0] - self.capital_costs
        after_tax_cash_flow[0] = after_tax_annual_costs[0]
        net_annual_costs_with_system[0] = after_tax_annual_costs[0]
        net_annual_costs_without_system[0] = 0

        # year 1 initializations
        annual_energy[1] = self.results.average_yearly_pv_energy_produced / self.econ.pv_levelization_factor
        bill_with_system[1] = self.year_one_bill
        bill_without_system[1] = self.year_one_bill_bau
        exports_with_system[1] = self.year_one_exports
        value_of_savings[1] = self.year_one_savings - self.year_one_exports
        o_and_m_capacity_cost[1] = self.econ.pv_om * self.pv_kw
        inflation_modifier = 1 + self.econ.rate_inflation + self.econ.rate_escalation

        federal_taxable_income_before_deductions[1] = self.federal_taxable_income_before_deductions(state_ibi, utility_ibi,
                                                                                             federal_cbi, state_cbi,
                                                                                             utility_cbi)

        for year in range(1, n_cols):

            inflation_modifier_n = inflation_modifier ** (year-1)
            degradation_modifier = 1 - self.econ.pv_degradation_rate

            if year > 1:

                # Annual energy
                annual_energy[year] = annual_energy[year - 1] * self.econ.pv_degradation_rate

                # Bill savings
                bill_without_system[year] = bill_without_system[year - 1] * inflation_modifier
                bill_with_system[year] = bill_with_system[year - 1] * inflation_modifier
                exports_with_system[year] = exports_with_system[year - 1] * inflation_modifier * degradation_modifier
                value_of_savings[year] = bill_without_system[year] - (bill_with_system[year] + exports_with_system[year])

                # Operating Expenses
                o_and_m_capacity_cost[year] = o_and_m_capacity_cost[year - 1] * inflation_modifier

            if self.econ.batt_replacement_year_kw == year:
                batt_kw_replacement_cost[year] = self.econ.batt_replacement_cost_kw * self.batt_kw * inflation_modifier_n

            if self.econ.batt_replacement_year_kwh == year:
                batt_kwh_replacement_cost[year] = self.econ.batt_replacement_cost_kwh * self.batt_kwh * inflation_modifier_n

            total_operating_expenses[year] = o_and_m_capacity_cost[year] + batt_kw_replacement_cost[year] + batt_kwh_replacement_cost[year]

            # Tax deductible operating expenses
            if self.econ.pv_macrs_schedule != 0:
                total_deductible_expenses[year] = total_operating_expenses[year]

            # Pre-tax cash flow
            pre_tax_cash_flow[year] = -(total_operating_expenses[year])

            # Direct cash incentives
            total_production_based_incentives[year] = self.pbi_calculate(year, annual_energy[year])

            # Federal income tax
            if year > 1 and self.pbi_combined_tax_fed:
                federal_taxable_income_before_deductions[year] = total_production_based_incentives[year]

            federal_itc_to_apply = 0
            if year == 1:
                federal_itc_to_apply = federal_itc

            federal_bonus_depreciation = 0
            if year == 1:
                federal_bonus_depreciation = self.econ.pv_macrs_bonus_fraction
            if year <= len(macrs_schedule):
                federal_depreciation_amount[year] = federal_depreciation_basis * (macrs_schedule[year - 1] + federal_bonus_depreciation)

            federal_total_deductions[year] = total_deductible_expenses[year] + federal_depreciation_amount[year]
            federal_income_tax[year] = (federal_taxable_income_before_deductions[year]-federal_total_deductions[year]) * self.fed_tax_owner
            federal_tax_liability[year] = -federal_income_tax[year] + federal_itc_to_apply

            # After tax calculation
            after_tax_annual_costs[year] = pre_tax_cash_flow[year] + \
                                           total_production_based_incentives[year] + \
                                           federal_tax_liability[year]

            after_tax_value_of_energy[year] = value_of_savings[year] * (1 - self.fed_tax_owner)
            after_tax_cash_flow[year] = after_tax_annual_costs[year] + after_tax_value_of_energy[year]

            net_annual_costs_without_system[year] = -bill_without_system[year] * (1 - self.fed_tax_owner)
            net_annual_costs_with_system[year] = after_tax_annual_costs[year] - (bill_with_system[year] + exports_with_system[year]) * (1 - self.fed_tax_owner)

        # Additional Unit test outputs
        self.fed_depr_basis_calc = federal_depreciation_basis
        self.fed_itc_basis_calc = federal_itc_basis
        self.federal_tax_liability = federal_tax_liability
        self.bill_with_sys = bill_with_system
        self.exports_with_sys = exports_with_system
        self.bill_bau = bill_without_system
        self.total_operating_expenses = total_operating_expenses
        self.after_tax_annual_costs = after_tax_annual_costs
        self.after_tax_value = after_tax_value_of_energy
        self.after_tax_cash_flow = after_tax_cash_flow
        self.net_annual_cost_without_sys = net_annual_costs_without_system
        self.net_annual_cost_with_sys = net_annual_costs_with_system

        # compute outputs
        try:
            self.irr = np.irr(after_tax_cash_flow)
        except ValueError:
            self.irr = 0
            log("ERROR", "IRR calculation failed to compute a real number")

        if math.isnan(self.irr):
            self.irr = 0

        self.npv = np.npv(self.econ.owner_discount_rate_nominal, after_tax_cash_flow)
        self.lcc = -np.npv(self.econ.owner_discount_rate_nominal, net_annual_costs_with_system)
        self.lcc_bau = -np.npv(self.econ.owner_discount_rate_nominal, net_annual_costs_without_system)

    def pbi_calculate(self, year, annual_energy):

        pbi_amount = 0
        if year <= self.pbi_combined_term:
            pbi_amount = min(self.pbi_combined_amount * annual_energy, self.pbi_combined_maxvalue)
        return pbi_amount

    def federal_taxable_income_before_deductions(self, state_ibi, utility_ibi, federal_cbi, state_cbi, utility_cbi):

        taxable_income = 0
        if self.ibi_sta_percent_tax_fed:
            taxable_income += state_ibi
        if self.ibi_uti_percent_tax_fed:
            taxable_income += utility_ibi
        if self.cbi_fed_tax_fed:
            taxable_income += federal_cbi
        if self.cbi_sta_tax_fed:
            taxable_income += state_cbi
        if self.cbi_uti_tax_fed:
            taxable_income += utility_cbi

        return taxable_income

    def federal_depreciation_basis(self, federal_itc, state_ibi, utility_ibi, federal_cbi, state_cbi, utility_cbi):

        basis = 0
        federal_deprecation = self.econ.pv_macrs_schedule
        itc_federal = 0

        if self.itc_fed_percent_deprbas_fed:
            itc_federal = self.econ.macrs_itc_reduction * federal_itc

        federal_itc_basis = self.federal_itc_basis(state_ibi, utility_ibi, federal_cbi, state_cbi, utility_cbi)
        basis = federal_itc_basis - itc_federal

        return basis

    def federal_itc_basis(self, state_ibi, utility_ibi, federal_cbi, state_cbi, utility_cbi):

        # reduce the itc basis
        ibi_state = 0
        ibi_util = 0
        cbi_fed = 0
        cbi_state = 0
        cbi_util = 0

        if self.ibi_sta_percent_deprbas_fed:
            ibi_state = state_ibi
        if self.ibi_uti_percent_deprbas_fed:
            ibi_util = utility_ibi
        if self.cbi_fed_deprbas_fed:
            cbi_fed = federal_cbi
        if self.cbi_sta_deprbas_fed:
            cbi_state = state_cbi
        if self.cbi_uti_deprbas_fed:
            cbi_util = utility_cbi

        return self.capital_costs - ibi_state - ibi_util - cbi_fed - cbi_state - cbi_util











