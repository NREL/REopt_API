#!/user/bin/python
# ==============================================================================
#  File: ~/sunlamp/DatLibrarySetup/mixed/economics.py
#  Date: June 30, 2016
#  Auth:  N. Laws
#
#  Description: creates economics in DatLibrary
#           Includes:   pwf_offtaker    == offtaker present worth factor
#                       pwf_owner       == owner present worth factor
#                       pwf_e           == electricity present worth factor
#                       pwf_om          == O&M present worth factor
#                       LevelizationFactor == used for PV ProdFactor
#                       OMperUnitSize
#                       CapCostSlope
#                       StorageCostPerKW
#                       StorageCostPerKWh
#                       ProdIncentRate
#                       MaxProdIncent
#                       MaxSizeForProdIncent
#           currently does not include passing any constants (eg discount rates)
# ==============================================================================
import os
from log_levels import log
import logging
from api_definitions import  *

def annuity(analysis_period, rate_escalation, rate_discount):
    '''this formulation assumes cost growth in first period
        i.e. it is a geometric sum of (1+rate_escalation)^n / (1+rate_discount)^n
        for n = 1,..., analysis_period
    '''
    if rate_escalation != rate_discount:
        x = (1 + rate_escalation) / (1 + rate_discount)
        pwf = round(x * (1 - x ** analysis_period) / (1 - x), 5)
    else:
        pwf = analysis_period
    return pwf


def annuity_degr(analysis_period, rate_escalation, rate_discount, rate_degradation):
    '''
    same as VBA Function PWaDegr(
    :param analysis_period: years
    :param rate_escalation: escalation rate
    :param rate_discount: discount rate
    :param rate_degradation: annual degradation
    :return: present worth factor with degradation
    '''
    pwf = 0
    for yr in range(1, analysis_period + 1):
        pwf += (1 + rate_escalation) ** yr / (1 + rate_discount) ** yr * (1 + rate_degradation) ** (yr - 1)
    return pwf


class Economics:

    macrs_five_year = [0.2, 0.32, 0.192, 0.1152, 0.1152, 0.0576]  # IRS pub 946
    macrs_seven_year = [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446]

    tech_size = 3 # [PV, PVNM, UTIL]
    bin_size = 4 # [R, W, X, S]

    def __init__(self, econ_inputs, file_path='economics.dat', business_as_usual=False):

        self.out_name = file_path
        self.business_as_usual = business_as_usual

        econ_list = inputs(filter="economics")
        for k in econ_list.keys():
            setattr(self, k, econ_inputs.get(k))

        # group outputs
        self.output_args = dict()
        self.incentive_output_args = dict()

        # set-up direct ownership
        if self.owner_discount_rate is None:
            self.owner_discount_rate = self.offtaker_discount_rate
        if self.owner_tax_rate is None:
            self.owner_tax_rate = self.offtaker_tax_rate

        # compute nominal discount rates
        self.offtaker_discount_rate_nominal = (1 + self.offtaker_discount_rate) * (1 + self.rate_inflation) - 1
        self.owner_discount_rate_nominal = (1 + self.owner_discount_rate) * (1 + self.rate_inflation) - 1
        self.rate_escalation_nominal = (1 + self.rate_escalation) * (1 + self.rate_inflation) - 1

        # initialize variables
        self.pv_macrs_schedule_array = list()
        self.batt_macrs_schedule_array = list()
        self.levelization_factor = 1
        self.output_args = dict()

        # tmp incentives
        self.macrs_itc_reduction = 0.5

        # run economics
        self.setup_macrs()
        self.setup_financial_parameters()
        self.setup_incentives()
        self.setup_business_as_usual()
        self.output_economics()

    def setup_macrs(self):

        self.pv_macrs_schedule_array = list()
        if self.pv_macrs_schedule == 5:
            self.pv_macrs_schedule_array = self.macrs_five_year
        elif self.pv_macrs_schedule == 7:
            self.pv_macrs_schedule_array = self.macrs_seven_year

        self.batt_macrs_schedule_array = list()
        if self.batt_macrs_schedule == 5:
            self.batt_macrs_schedule_array = self.macrs_five_year
        elif self.batt_macrs_schedule_array == 7:
            self.batt_macrs_schedule_array = self.macrs_seven_year

    def setup_financial_parameters(self):

        self.output_args['analysis_period'] = self.analysis_period
        self.output_args['pwf_owner'] = annuity(self.analysis_period, 0, self.owner_discount_rate)
        self.output_args['pwf_offtaker'] = annuity(self.analysis_period, 0, self.offtaker_discount_rate)
        self.output_args['pwf_om'] = annuity(self.analysis_period, self.rate_inflation, self.owner_discount_rate_nominal)
        self.output_args['pwf_e'] = annuity(self.analysis_period, self.rate_escalation_nominal, self.offtaker_discount_rate_nominal)
        self.output_args['pwf_op'] = annuity(self.analysis_period, self.rate_escalation_nominal, self.owner_discount_rate_nominal)
        self.output_args['r_tax_offtaker'] = self.offtaker_tax_rate
        self.output_args['r_tax_owner'] = self.owner_tax_rate
        self.output_args["OMperUnitSize"] = self.pv_om
        if self.output_args['pwf_owner'] == 0 or self.output_args['r_tax_owner'] ==0:
            self.output_args['two_party_factor'] = 0
        else:    
            self.output_args['two_party_factor'] = (self.output_args['pwf_offtaker'] * self.output_args['r_tax_offtaker']) / (self.output_args['pwf_owner'] * self.output_args['r_tax_owner'])

        # compute degradation impact
        self.levelization_factor = round(annuity_degr(self.analysis_period, self.rate_escalation, self.offtaker_discount_rate,
                           - self.pv_degradation_rate) / self.output_args["pwf_e"], 5)

        self.output_args['LevelizationFactor'] = self.levelization_factor

    def setup_incentives(self):

        self.output_args["CapCostSlope"] = self.setup_capital_cost_incentive(self.pv_cost,
                                                                             0,
                                                                             self.analysis_period,
                                                                             self.owner_discount_rate_nominal,
                                                                             self.owner_tax_rate,
                                                                             self.pv_itc_federal,
                                                                             self.pv_itc_federal_max,
                                                                             self.pv_rebate_federal,
                                                                             self.pv_rebate_federal_max,
                                                                             self.pv_macrs_schedule_array,
                                                                             self.pv_macrs_bonus_fraction,
                                                                             self.macrs_itc_reduction)
        self.output_args["StorageCostPerKW"] = self.setup_capital_cost_incentive(self.batt_cost_kw,
                                                                                 self.batt_replacement_cost_kw,
                                                                                 self.batt_replacement_year_kw,
                                                                                 self.owner_discount_rate_nominal,
                                                                                 self.owner_tax_rate,
                                                                                 self.batt_itc_federal,
                                                                                 self.batt_itc_federal_max,
                                                                                 self.batt_rebate_federal,
                                                                                 self.batt_rebate_federal_max,
                                                                                 self.batt_macrs_schedule_array,
                                                                                 self.batt_macrs_bonus_fraction,
                                                                                 self.macrs_itc_reduction)
        self.output_args["StorageCostPerKWH"] = self.setup_capital_cost_incentive(self.batt_cost_kwh,
                                                                                  self.batt_replacement_cost_kwh,
                                                                                  self.batt_replacement_year_kwh,
                                                                                  self.owner_discount_rate_nominal,
                                                                                  self.owner_tax_rate,
                                                                                  self.batt_itc_federal,
                                                                                  self.batt_itc_federal_max,
                                                                                  self.batt_rebate_federal,
                                                                                  self.batt_rebate_federal_max,
                                                                                  self.batt_macrs_schedule_array,
                                                                                  self.batt_macrs_bonus_fraction,
                                                                                  self.macrs_itc_reduction)
        for tech in range(0, 2):
            self.setup_production_incentive(tech,
                                            self.rate_escalation_nominal,
                                            self.offtaker_discount_rate_nominal,
                                            self.pv_pbi,
                                            self.pv_pbi_max,
                                            min(self.pv_pbi_system_max,self.pv_kw_max),
                                            self.pv_pbi_years)

    @staticmethod
    def setup_capital_cost_incentive(tech_cost, replacement_cost, replacement_year,
                                     discount_rate, tax_rate,
                                     itc, itc_max,
                                     rebate, rebate_max,
                                     macrs_schedule, macrs_bonus_fraction, macrs_itc_reduction):

        ''' effective PV and battery prices with ITC and depreciation
            (i) depreciation tax shields are inherently nominal --> no need to account for inflation
            (ii) ITC and bonus depreciation are taken at end of year 1
            (iii) battery replacement cost: one time capex in user defined year discounted back to t=0 with r_owner
        '''

        basis = tech_cost * (1 - macrs_itc_reduction * itc)
        bonus = basis * macrs_bonus_fraction * tax_rate
        macrs_base = basis * (1 - macrs_bonus_fraction)

        tax_shield = 0
        for idx, r in enumerate(macrs_schedule):  # tax shields are discounted to year zero
            tax_shield += r * macrs_base * tax_rate / (1 + discount_rate) ** (idx + 1)

        cap_cost_slope = tech_cost - tax_shield - itc * tech_cost / (1 + discount_rate) - bonus / (1 + discount_rate)
        cap_cost_slope += replacement_cost / (1 + discount_rate) ** replacement_year

        return round(cap_cost_slope, 4)

    def setup_production_incentive(self, tech, rate_escalation, rate_discount, pbi, pbi_max, pbi_system_max, pbi_years):

        pwf_prod_incent = annuity(pbi_years, rate_escalation, rate_discount)
        prod_incent_rate = round(pbi, 3)
        max_prod_incent = round(pbi_max, 3)
        max_size_for_prod_incent = pbi_system_max

        if "ProdIncentRate" not in self.incentive_output_args:
            prod_incent_array = self.tech_size * self.bin_size * [0]
        else:
            prod_incent_array = self.incentive_output_args["ProdIncentRate"]

        if "MaxProdIncent" not in self.incentive_output_args:
            max_prod_array = self.tech_size * [0]
        else:
            max_prod_array = self.incentive_output_args["MaxProdIncent"]

        if "MaxSizeForProdIncent" not in self.incentive_output_args:
            max_size_array = self.tech_size * [0]
        else:
            max_size_array = self.incentive_output_args["MaxSizeForProdIncent"]

        for i in range(tech * self.bin_size, (tech + 1) * self.bin_size):
            prod_incent_array[i] = prod_incent_rate

        max_prod_array[tech] = max_prod_incent
        max_size_array[tech] = max_size_for_prod_incent

        self.output_args["pwf_prod_incent"] = pwf_prod_incent
        self.incentive_output_args["ProdIncentRate"] = prod_incent_array
        self.incentive_output_args["MaxProdIncent"] = max_prod_array
        self.incentive_output_args["MaxSizeForProdIncent"] = max_size_array

    def setup_business_as_usual(self):
        if self.business_as_usual:

            self.output_args['CapCostSlope'] = 0
            self.output_args['LevelizationFactor'] = 1.0
            self.output_args['OMperUnitSize'] = 0

            self.incentive_output_args['ProdIncentRate'] = 4 * [0]
            self.incentive_output_args['MaxProdIncent'] = [0]
            self.incentive_output_args['MaxSizeForProdIncent'] = [0]

    def output_economics(self):

        args = self.output_args
        incentive_args = self.incentive_output_args

        with open(self.out_name, 'w') as f:
            key = args.iterkeys()
            value = args.itervalues()
            for _ in range(len(args)):
                try:
                    k = key.next()
                    v = value.next()
                    f.write(k + ': [\n')
                    f.write(str(v) + ',\n')
                    if not self.business_as_usual:
                        if "CapCostSlope" in k:  # need additional lines for each TECH: [PV, PVNM, UTIL]
                            f.write(str(v) + ',\n')
                            f.write(str(0) + ',\n')
                        if "OMperUnitSize" in k:  # need additional lines for each TECH: [PV, PVNM, UTIL]
                            f.write(str(v) + ',\n')
                            f.write(str(0) + ',\n')
                        if "LevelizationFactor" in k:  # need additional lines for each TECH: [PV, PVNM, UTIL]
                            f.write(str(v) + ',\n')
                            f.write(str(1.0) + ',\n')
                    f.write(']\n')
                except:
                    print '\033[91merror writing economics\033[0m'

            key = incentive_args.iterkeys()
            value = incentive_args.itervalues()
            for _ in range(len(incentive_args)):
                try:
                    k = key.next()
                    v = value.next()
                    f.write(k + ': [\n')
                    for val in v:
                        f.write(str(val) + ',\n')
                    f.write(']\n')
                except:
                    print '\033[91merror writing economics\033[0m'

