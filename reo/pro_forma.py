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
import math
from xlsxwriter.utility import xl_rowcol_to_cell as cvt

from log_levels import log

class ProForma(object):
    """
    Creates Excel spreadsheet with discounted cash flow analysis.

    Default values set to Sunlamp base case values.
    Assumes 5 year MACRS and battery+inverter replacement in year 10.

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
        :param batt_repl: default=200 $/kWh
        :param invt_repl: default=200 $/kW
        :param pv_degredation: %/yr of pv production degredation, default = 0.005 (0.5%/yr)
        :param lcc: Life Cycle Cost
        :param lcc_bau: business as usual Life Cycle Cost
    """

    macrs_schedule = [0.2, 0.32, 0.192, 0.1152, 0.1152, 0.0576]  # IRS pub 946

    def __init__(self, analysis_period=25,
                 discount_rate=0.08,
                 tax_rate=0.35,
                 bonus_fraction=0.5,
                 itc_fraction=0.3,
                 elec_escalation=0.0039,
                 inflation=0.02,
                 om_cost=20,
                 pv_cost=2160,
                 pv_size=0,
                 batt_cost=500,
                 batt_capacity=0,
                 invt_cost=1600,
                 invt_size=0,
                 batt_repl=200,
                 invt_repl=200,
                 energy_savings_yr1=0,
                 demand_savings_yr1=0,
                 export_benefit_yr1=0,
                 pv_degredation=0.005,
                 lcc=0,
                 lcc_bau=0,
                 ):

        self.analysis_period = int(analysis_period)
        self.discount_rate = discount_rate
        self.tax_rate = tax_rate
        self.bonus_fraction = bonus_fraction
        self.itc_fraction = itc_fraction
        self.elec_escalation = elec_escalation
        self.inflation = inflation
        self.om_cost = om_cost
        self.pv_cost = pv_cost
        self.pv_size = float(pv_size)
        self.batt_cost = float(batt_cost)
        self.batt_capacity = float(batt_capacity)
        self.invt_cost = invt_cost
        self.invt_size = float(invt_size)
        self.batt_repl = batt_repl
        self.invt_repl = invt_repl
        self.energy_savings_yr1 = float(energy_savings_yr1)
        self.demand_savings_yr1 = float(demand_savings_yr1)
        self.export_benefit_yr1 = float(export_benefit_yr1)
        self.pv_degredation = pv_degredation
        self.lcc = lcc
        self.lcc_bau = lcc_bau

        self.IRR = 0
        self.NPV = 0

        self.inputs = (
            ['discount rate (nominal)', self.discount_rate],
            ['tax rate', self.tax_rate],
            ['bonus fraction', self.bonus_fraction],
            ['ITC fraction', self.itc_fraction],
            ['electricity escalation (nominal)', self.elec_escalation],
            ['inflation rate', self.inflation],
            ['----------------', '----------------'],
            ['PV capacity (kW)', self.pv_size],
            ['Battery capacity (kWh)', self.batt_capacity],
            ['Battery power (kW)', self.invt_size],
            ['----------------', '----------------'],
            ['PV cost, installed ($/kW)', self.pv_cost],
            ['Battery cost ($/kWh)', self.batt_cost],
            ['Battery inverter cost ($/kW)', self.invt_cost],
            ['PV 0&M ($/kW/yr)', self.om_cost],
            ['Battery replacement cost ($/kWh)', self.batt_repl],
            ['Inverter replacement cost ($/kW)', self.invt_repl],
            ['----------------', '----------------'],
            ['Year 1 energy savings', self.energy_savings_yr1],
            ['Year 1 demand savings', self.demand_savings_yr1],
            ['Year 1 export benefit', self.export_benefit_yr1],
            ['PV degradation (%/year)', self.pv_degredation],
            ['analysis_period', self.analysis_period]
        )

        '''
        row_cash_flows = row where "Cash Flows" is written.
        Below this row is where all lines of the DCF are written.
        '''
        row_cash_flows = len(self.inputs) + 2

        self.cash_flow_rows = [  # these strings are printed to spreadsheet in this order
            'Year',
            'Capex',
            'O&M (PV)',
            'Battery Replacement Cost',
            'Energy Bill Savings',
            'Demand Bill Savings',
            'Energy Export Benefit',
            'Depreciation Tax Shield',
            'ITC',
            'Bonus Tax Shield',
            'After Tax Bill Savings',
            'After Tax O&M',
            'Free Cash Flow',
            'Discounted Cash Flow',
            '',
            'NPV',
            'IRR',
            'LCC (with system)',
            'LCC (without system)',
        ]

        rows = dict()
        rows['year'] = row_cash_flows + 1
        rows['capex'] = row_cash_flows + 2
        rows['om'] = row_cash_flows + 3
        rows['batt_repl'] = row_cash_flows + 4
        rows['Esavings'] = row_cash_flows + 5
        rows['Dsavings'] = row_cash_flows + 6
        rows['export'] = row_cash_flows + 7
        rows['deprTaxShield'] = row_cash_flows + 8
        rows['ITC'] = row_cash_flows + 9
        rows['bonus'] = row_cash_flows + 10
        rows['afterTaxEsavings'] = row_cash_flows + 11
        rows['afterTaxOM'] = row_cash_flows + 12
        rows['FCF'] = row_cash_flows + 13
        rows['DCF'] = row_cash_flows + 14
        # blank row
        rows['NPV'] = row_cash_flows + 16
        rows['IRR'] = row_cash_flows + 17
        rows['LCC'] = row_cash_flows + 18
        rows['LCC_bau'] = row_cash_flows + 19


        self.row_cash_flows = row_cash_flows
        self.rows = rows

    def make_pro_forma(self, path_file):

        cells = {
            'deprBasis': 'E2',
            'discountRate': 'B2',
            'taxRate': 'B3',
            'bonusFraction': 'B4',
            'ITCfraction': 'B5',
            'esce': 'B6',
            'inflation': 'B7',
            'pvSize': 'B9',
            'battSize': 'B10',
            'invtSize': 'B11',
            'pvCost': 'B13',
            'battCost': 'B14',
            'invtCost': 'B15',
            'pvOM': 'B16',
            'battReplCost': 'B17',
            'invtReplCost': 'B18',
            'yr1Esavings': 'B20',
            'yr1Dsavings': 'B21',
            'yr1ExportBen': 'B22',
            'pvDegredation': 'B23',
            'years': 'B24',
        }

        self.initialize_workbook(path_file)
        self.compute_IRR()

        currency = self.book.add_format({'num_format': '$#,##0'})
        percent = self.book.add_format({'num_format': '0.00%'})

        capex = '=-(' + cells['pvSize']   + '*' + cells['pvCost'] + '+'   \
                      + cells['battSize'] + '*' + cells['battCost'] + '+' \
                      + cells['invtSize'] + '*' + cells['invtCost'] \
                      + ')'

        basis = '=-' + cvt(self.rows['capex'], 1) + '-0.5*' + cvt(self.rows['ITC'], 2)

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
            # depreciation
            self.sheet.write(row, col, '=$F$6*' + cvt(3, col), currency)
            # end. book value
            self.sheet.write(row + 1, col, '=' + cvt(5, col) + '-' + cvt(6, col), currency)

        # discounted cash flow
        npv_formula = '=SUM(' + cvt(self.rows['DCF'], 1) + ':' + cvt(self.rows['DCF'], self.analysis_period+1) + ')'
        irr_formula = '=IRR(' + cvt(self.rows['FCF'], 1) + ':' + cvt(self.rows['FCF'], self.analysis_period+1) + ')'
        batt_repl_formula = '=-(' + cells['battSize'] + '*' + cells['battReplCost'] + '+' \
                                  + cells['invtSize'] + '*' + cells['invtReplCost'] \
                            + ')'
        bonus_formula = '=' + cells['deprBasis'] + '*' + cells['bonusFraction'] + '*' + cells['taxRate']
        ITC_formula = '=-' + cells['ITCfraction'] + '*' + cvt(self.rows['capex'], 1)

        self.sheet.write(cvt(self.rows['capex'], 1),      capex,               currency)
        self.sheet.write(cvt(self.rows['batt_repl'], 11), batt_repl_formula, currency)  # battery replacement in year 10
        self.sheet.write(cvt(self.rows['ITC'],   2),      ITC_formula,         currency)
        self.sheet.write(cvt(self.rows['bonus'], 2),      bonus_formula,       currency)  # Bonus tax shield
        self.sheet.write(cvt(self.rows['DCF'],   1),      '=' + cvt(self.rows['FCF'], 1), currency)  # no discount in year zero
        self.sheet.write(cvt(self.rows['NPV'],   1),      npv_formula,  currency)  # NPV
        self.sheet.write(cvt(self.rows['IRR'],   1),      irr_formula,  percent, self.IRR)  # IRR
        self.sheet.write(cvt(self.rows['LCC'],   1),      self.lcc,  currency)  # LCC
        self.sheet.write(cvt(self.rows['LCC_bau'],   1),  self.lcc_bau,  currency)  # LCC BAU


        om_formula = '=-$B$16*$B$9*(1+$B$7)^'
        energy_formula = '=$B$20*(1+$B$6)^'
        demand_formula = '=$B$21*(1+$B$6)^'
        export_formula = ['=$B$22*(1+$B$6)^', '*(1-$B$23)^']
        tax_formula = '=(1-$B$3)*'
        depr_formula = '=$B$3*'
        dcf_formula = '/(1+$B$2)^'

        # fill out cash flow columns
        for col in range(1, self.analysis_period + 2):

            # free cash flow
            self.sheet.write(self.rows['FCF'], col, '=' + cvt(self.rows['capex'], col) + '+' + cvt(self.rows['batt_repl'], col) + '+' +
                             'SUM(' + cvt(self.rows['deprTaxShield'], col) + ':' + cvt(self.rows['afterTaxOM'], col) + ')', currency)
            if col > 1:
                self.sheet.write(self.rows['om'],               col, om_formula     + cvt(self.rows['year'], col), currency)
                self.sheet.write(self.rows['Esavings'],         col, energy_formula + cvt(self.rows['year'], col), currency)
                self.sheet.write(self.rows['Dsavings'],         col, demand_formula + cvt(self.rows['year'], col), currency)

                self.sheet.write(self.rows['export'],           col, export_formula[0] + cvt(self.rows['year'], col) + export_formula[1] + cvt(self.rows['year'], col-1), currency)

                self.sheet.write(self.rows['afterTaxEsavings'], col, tax_formula    + '(' + cvt(self.rows['Esavings'], col) + '+' + cvt(self.rows['Dsavings'], col) + '+' + cvt(self.rows['export'], col) + ')', currency)
                self.sheet.write(self.rows['afterTaxOM'],       col, tax_formula    + cvt(self.rows['om'], col), currency)
                self.sheet.write(self.rows['DCF'],              col, '=' + cvt(self.rows['FCF'], col) + dcf_formula + cvt(self.rows['year'], col), currency)

                # depreciation tax shield
                if col < len(self.macrs_schedule) + 2:
                    self.sheet.write(self.rows['deprTaxShield'], col, depr_formula + cvt(6, col + 3), currency)

        self.book.close()

    def initialize_workbook(self, path_file):

        book = xlsxwriter.Workbook(path_file)
        sheet = book.add_worksheet('Cash Flow')
        bold = book.add_format({'bold': 1})

        sheet.write('A1', 'Inputs can be changed here', bold)
        sheet.write('D1', 'Depreciation Schedule', bold)
        sheet.set_column(1, 0, self.analysis_period + 1)  # (sheet, column, width)
        sheet.set_column(1, 1, 12)
        for col in range(2, self.analysis_period + 2):
            sheet.set_column(1, col, 10)

        sheet.write(cvt(self.row_cash_flows, 0), 'Cash Flows', bold)

        # rows and cols indexed on zero
        row = 1
        col = 0

        # print input names and values
        for name, val in self.inputs:
            sheet.write_string(row, col, name)
            if isinstance(val, (int, float)):
                sheet.write_number(row, col + 1, val)
            else:
                sheet.write_string(row, col + 1, val)
            row += 1

        # print cash_flow_rows
        row = self.row_cash_flows + 1
        col = 0
        for name in self.cash_flow_rows:
            sheet.write_string(row, col, name)
            row += 1

        # year integers
        row = self.row_cash_flows + 1
        col = 1
        for y in range(self.analysis_period + 1):
            sheet.write_number(row, col, y)
            col += 1
        self.book = book
        self.sheet = sheet

    def get_IRR(self):
        return self.IRR

    def compute_IRR(self):

        # capital costs
        capital_costs = self.pv_size * self.pv_cost + self.batt_capacity * self.batt_cost + self.invt_size * self.invt_cost

        # depreciable basis
        ITC = self.itc_fraction * capital_costs
        depreciable_basis = capital_costs - 0.5 * ITC

        years = self.analysis_period + 1

        om_costs = years * [0]
        electricity_savings = years * [0]
        om_costs_after_tax = years * [0]
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
                om_costs[year] = -self.om_cost * self.pv_size * (1 + self.inflation) ** year
                electricity_savings[year] = (self.energy_savings_yr1 + self.demand_savings_yr1) * (1 + self.elec_escalation) ** year

            if year == 10:
                battery_replacement[year] = -self.batt_repl * (self.invt_size + self.batt_capacity)

            om_costs_after_tax[year] = om_costs[year] * (1 - self.tax_rate)
            electricity_savings_after_tax[year] = electricity_savings[year] * (1 - self.tax_rate)

            free_cash_flow[year] += depreciation_tax_shield[year] * self.tax_rate + \
                                    battery_replacement[year] + \
                                    om_costs_after_tax[year] + \
                                    electricity_savings_after_tax[year]

            discounted_cash_flow[year] = free_cash_flow[year] / ((1 + self.discount_rate) ** year)

        self.NPV = sum(discounted_cash_flow)
        self.IRR = np.irr(free_cash_flow)

        if math.isnan(self.IRR):
            self.IRR = 0
            log("WARNING", "Computed IRR invalid")
        if math.isnan(self.NPV):
            self.NPV = 0
            log("WARNING", "Computed NPV invalid")
