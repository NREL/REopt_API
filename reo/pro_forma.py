#!/user/bin/python
# ==============================================================================
#  File: ~\Sunlamp\AnalyzeResults\ProForma\pro_forma.py
#  Date: August 31, 2016
#  Auth: N. Laws
#
#  Description: builds Excel sheet discounted-cash-flow analysis using REopt output
#
# ==============================================================================
import os
import xlsxwriter
import numpy as np
from xlsxwriter.utility import xl_rowcol_to_cell as cvt


class ProForma(object):
    '''
    creates Excel spreadsheet with discounted cash flow analysis for a given scenario
    '''

    macrs_schedule = [0.2, 0.32, 0.192, 0.1152, 0.1152, 0.0576]  # IRS pub 946

    def __init__(self, analysis_period=25, discount_rate=0.08, tax_rate=0.35, bonus_fraction=0.5, itc_fraction=0.3, elec_escalation=0.0039, \
                 inflation=0.02, om_cost=20, pv_cost=2160, batt_cost=500, invt_cost=1600, batt_repl=200):
        '''
        Default values set to Sunlamp base case values. Assumes 5 year MACRS.
        :param analysis_period: default=25
        :param discount_rate: default=0.08 (real discount rate)
        :param tax_rate: default=0.35
        :param bonus_fraction: default=0.5
        :param itc_fraction: default=0.3
        :param elec_escalation: default=0.0039 (real escalation rate)
        :param inflation: default=0.02
        :param om_cost: default=20 $/kW/year (PV only)
        :param pv_cost: default=2160 $/kW
        :param batt_cost: default=500 $/kWh
        :param invt_cost: default=1600 $/kW
        :param batt_repl: default=200 $/kW and $/kWh (for both battery and inverter)

        '''
        self.analysis_period = int(analysis_period)
        self.discount_rate = discount_rate
        self.tax_rate = tax_rate
        self.bonus_fraction = bonus_fraction
        self.itc_fraction = itc_fraction
        self.elec_escalation = elec_escalation
        self.inflation = inflation
        self.om_cost = om_cost
        self.pv_cost = pv_cost
        self.batt_cost = float(batt_cost)
        self.invt_cost = invt_cost
        self.batt_repl = batt_repl
        self.IRR = 0
        self.NPV = 0

    def dcf(self, path_file, pv_size=0, batt_capacity=0, batt_power=0, \
            energy_savings_yr1=0, demand_savings_yr1=0):

        self.pv_size = float(pv_size)
        self.batt_capacity = float(batt_capacity)
        self.batt_power = float(batt_power)
        self.energy_savings_yr1 = float(energy_savings_yr1)
        self.demand_savings_yr1 = float(demand_savings_yr1)

        self.initialize_workbook(path_file)
        self.compute_cash_flow()

        currency = self.book.add_format({'num_format': '$#,##0'})
        percent = self.book.add_format({'num_format': '0.00%'})

        capex = '=-(B9*B13+B10*B14+B11*B15)'
        basis = '=-B25-0.5*C31'

        # depreciation schedule
        self.sheet.write('D4', 'MACRS schedule')
        self.sheet.write('D2', 'depr. basis')
        self.sheet.write('E2', basis, currency)
        self.sheet.write('F2',
                         'NOTE: If you claim the 30% ITC then the depreciable amount is reduced by 1/2 of the ITC credit')
        self.sheet.write('F5', 'NOTE: scheduled depreciation basis reduced by the bonus deprecation')
        self.sheet.write('E3', 'year')
        row = 2
        col = 5
        for y in range(1, 7):
            self.sheet.write(row, col, y)
            self.sheet.write(row + 1, col, self.macrs_schedule[y - 1])
            col += 1
        self.sheet.write('D6', 'beg. book value')
        self.sheet.write('D7', 'depreciation')
        self.sheet.write('D8', 'end. book value')
        self.sheet.write('F6', '=E2-B4*E2', currency)  # year 1 book value
        row = 6
        for col in range(5, 11):
            if col > 5:
                self.sheet.write(row - 1, col, '=' + cvt(7, col - 1), currency)
            self.sheet.write(row, col, '=$F$6*' + cvt(3, col), currency)
            self.sheet.write(row + 1, col, '=' + cvt(5, col) + '-' + cvt(6, col), currency)

        # cash flows
        self.sheet.write('B25', capex, currency)
        self.sheet.write('C31', '=-B5*B25', currency)  # ITC
        self.sheet.write('C32', '=E2*B4*B3', currency)  # Bonus tax shield
        self.sheet.write('B36', '=B35', currency)  # no discount in year zero
        self.sheet.write('B38', '=SUM(B36:AA36)', currency)  # NPV
        self.sheet.write('B39', '=IRR(B35:AA35)', percent, self.IRR)  # IRR
        self.sheet.write('L27', '=-B17*(B10+B11)', currency)  # battery replacement in year 10
        om_formula = '=-$B$16*$B$9*(1+$B$7)^'
        energy_formula = '=$B$19*(1+$B$6)^'
        demand_formula = '=$B$20*(1+$B$6)^'
        tax_formula = '=(1-$B$3)*'
        depr_formula = '=$B$3*'
        dcf_formula = '/(1+$B$2)^'
        row = 24  # capex row
        for col in range(1, self.analysis_period + 2):
            self.sheet.write(row + 10, col, '=' + cvt(row, col) + '+' + cvt(row + 2, col) + '+' +
                             'SUM(' + cvt(row + 5, col) + ':' + cvt(row + 9, col) + ')', currency)
            if col > 1:
                self.sheet.write(row + 1, col, om_formula + cvt(row - 1, col), currency)
                self.sheet.write(row + 3, col, energy_formula + cvt(row - 1, col), currency)
                self.sheet.write(row + 4, col, demand_formula + cvt(row - 1, col), currency)
                self.sheet.write(row + 8, col, tax_formula + '(' + cvt(row + 3, col) + '+' + cvt(row + 4, col) + ')', currency)
                self.sheet.write(row + 9, col, tax_formula + cvt(row + 1, col), currency)
                self.sheet.write(row + 11, col, '=' + cvt(row + 10, col) + dcf_formula + cvt(row - 1, col), currency)
                if col < len(self.macrs_schedule) + 2:
                    self.sheet.write(row + 5, col, depr_formula + cvt(6, col + 3), currency)

        self.book.close()

    def initialize_workbook(self, path_file):

        book = xlsxwriter.Workbook(path_file)
        sheet = book.add_worksheet('Cash Flow')
        bold = book.add_format({'bold': 1})

        sheet.write('A1', 'Inputs can be changed here', bold)
        sheet.write('D1', 'Depreciation Schedule', bold)
        sheet.write('A23', 'Cash Flows', bold)
        sheet.set_column(1, 0, self.analysis_period + 1)  # (sheet, column, width)
        sheet.set_column(1, 1, 12)
        for col in range(2, self.analysis_period + 2):
            sheet.set_column(1, col, 10)

        inputs = (
            ['discount rate (nominal)', self.discount_rate],
            ['tax rate', self.tax_rate],
            ['bonus fraction', self.bonus_fraction],
            ['ITC fraction', self.itc_fraction],
            ['electricity escalation (nominal)', self.elec_escalation],
            ['inflation rate', self.inflation],
            ['----------------', '----------------'],
            ['PV capacity (kW)', self.pv_size],
            ['Battery capacity (kWh)', self.batt_capacity],
            ['Battery power (kW)', self.batt_power],
            ['----------------', '----------------'],
            ['PV cost, installed ($/kW)', self.pv_cost],
            ['Battery cost ($/kWh)', self.batt_cost],
            ['Battery inverter cost ($/kW)', self.invt_cost],
            ['PV 0&M ($/kW/yr)', self.om_cost],
            ['Battery replacement cost', self.batt_repl],
            ['----------------', '----------------'],
            ['Year 1 energy savings', self.energy_savings_yr1],
            ['Year 1 demand savings', self.demand_savings_yr1],
            ['analysis_period', self.analysis_period]
        )

        cash_flow_rows = [
            'Year',
            'Capex',
            'O&M (PV)',
            'Battery Replacement',
            'Energy Cost Savings',
            'Demand Cost Savings',
            'Depreciation Tax Shield',
            'ITC',
            'Bonus Tax Shield',
            'After Tax Electricity Savings',
            'After Tax O&M',
            'Free Cash Flow',
            'Discounted Cash Flow',
            '',
            'NPV',
            'IRR'
        ]

        # rows and cols indexed on zero
        row = 1
        col = 0

        for name, val in (inputs):
            sheet.write_string(row, col, name)
            if isinstance(val, (int, float)):
                sheet.write_number(row, col + 1, val)
            else:
                sheet.write_string(row, col + 1, val)
            row += 1

        row = 23
        col = 0
        for name in cash_flow_rows:
            sheet.write_string(row, col, name)
            row += 1

        row = 23
        col = 1
        for y in range(self.analysis_period + 1):
            sheet.write_number(row, col, y)
            col += 1
        self.book = book
        self.sheet = sheet

    def compute_cash_flow(self):

        # capital costs
        capital_costs = self.pv_size * self.pv_cost + self.batt_capacity * self.batt_cost + self.batt_power * self.invt_cost

        # depreciable basis
        ITC = self.itc_fraction * capital_costs
        depreciable_basis = capital_costs - 0.5 * ITC

        depreciation = []


        years = self.analysis_period + 1

        o_and_m_costs = years * [0]
        electricity_savings = years * [0]
        o_and_m_costs_after_tax = years * [0]
        electricity_savings_after_tax = years * [0]
        battery_replacement = years * [0]
        free_cash_flow = years * [0]
        discounted_cash_flow = years * [0]
        depreciation_tax_shield = years * [0]

        beginning_book_value_year_1 = 0
        beginning_book_value = 0

        for year in range(1, len(self.macrs_schedule) + 1):
            macrs_fraction = self.macrs_schedule[year - 1]

            if year == 1:
                beginning_book_value_year_1 = depreciable_basis * (1 - self.bonus_fraction)
            else:
                beginning_book_value = end_book_value

            depreciation_tax_shield[year] = beginning_book_value_year_1 * macrs_fraction

            if year == 1:
                end_book_value = beginning_book_value_year_1 - depreciation_tax_shield[year]
            else:
                end_book_value = beginning_book_value - depreciation_tax_shield[year]

        for year in range(0, years):

            # Capital costs
            if year == 0:
                free_cash_flow[year] = -capital_costs
                discounted_cash_flow[year] = -capital_costs

            # bonus depreciation and ITC
            if year == 1:
                free_cash_flow[year] += ITC
                free_cash_flow[year] += self.bonus_fraction * self.tax_rate * depreciable_basis

            if year > 0:
                o_and_m_costs[year] = -self.om_cost * self.pv_size * (1 + self.inflation) ** year
                electricity_savings[year] = (self.energy_savings_yr1 + self.demand_savings_yr1) * (1 + self.elec_escalation) ** year


            if year == 10:
                battery_replacement[year] = -self.batt_repl * (self.batt_power + self.batt_capacity)

            o_and_m_costs_after_tax[year] = o_and_m_costs[year] * (1 - self.tax_rate)
            electricity_savings_after_tax[year] = electricity_savings[year] * (1 - self.tax_rate)

            free_cash_flow[year] += depreciation_tax_shield[year] * self.tax_rate + \
                                   battery_replacement[year] + \
                                   o_and_m_costs_after_tax[year] + \
                                   electricity_savings_after_tax[year]

            discounted_cash_flow[year] = free_cash_flow[year] / ((1 + self.discount_rate) ** year)

        self.NPV = sum(discounted_cash_flow)

        if self.NPV > 0 and (self.pv_size > 0 or self.batt_capacity > 0 or self.batt_power > 0):
            self.IRR = np.irr(free_cash_flow)






