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
from api_definitions import *
from utilities import write_single_variable

def slope(x1, y1, x2, y2):
    return (y2 - y1) / (x2 - x1)

def intercept(x1, y1, x2, y2):
    return y2 - slope(x1, y1, x2, y2) * x2

def annuity(analysis_period, rate_escalation, rate_discount):
    '''this formulation assumes cost growth in first period
        i.e. it is a geometric sum of (1+rate_escalation)^n / (1+rate_discount)^n
        for n = 1,..., analysis_period
    '''
    x = (1 + rate_escalation) / (1 + rate_discount)
    if x != 1:
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

    tech_size = 3
    techs = ['PV', 'PVNM', 'UTIL']
    tech_size_bau = 1
    techs_bau = ['UTIL']
    bin_size = 4
    bins = ['R', 'W', 'X', 'S']

    def __init__(self, econ_inputs, file_path='economics.dat', business_as_usual=False):

        self.out_name = file_path
        self.business_as_usual = business_as_usual

        econ_list = inputs(filter="economics")
        for k in econ_list.keys():
            setattr(self, k, econ_inputs.get(k))

        # group outputs
        self.output_args = dict()

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
        self.pv_levelization_factor = 1

        # cost curve
        self.xp_array_incent = list()
        self.yp_array_incent = list()
        self.cap_cost_slope = list()
        self.cap_cost_yint = list()
        self.cap_cost_x = list()
        self.cap_cost_segments = 1

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

        if self.output_args['pwf_owner'] == 0 or self.output_args['r_tax_owner'] == 0:
            self.output_args['two_party_factor'] = 0
        else:    
            self.output_args['two_party_factor'] = (self.output_args['pwf_offtaker'] * self.output_args['r_tax_offtaker']) / (self.output_args['pwf_owner'] * self.output_args['r_tax_owner'])

        # compute degradation impact
        if self.output_args['pwf_e'] == 0:
            self.pv_levelization_factor = 0
        else:
            lf = annuity_degr(self.analysis_period, self.rate_escalation, self.offtaker_discount_rate, -self.pv_degradation_rate) / self.output_args["pwf_e"]
            self.pv_levelization_factor = round(lf, 5)

        levelization_factor_array = list()
        for t in self.techs:
            if t == 'PV' or 'PVNM':
                levelization_factor_array.append(self.pv_levelization_factor)
            else:
                levelization_factor_array.append(1.0)

        self.output_args['LevelizationFactor'] = levelization_factor_array

    def insert_u_bp(self, u_xbp, u_ybp, p, u_cap):

        self.xp_array_incent.append(u_xbp)
        self.yp_array_incent.append(u_ybp - u_ybp * p + u_cap)

    def insert_p_bp(self, p_xbp, p_ybp, u, p_cap):

        self.xp_array_incent.append(p_xbp)
        self.yp_array_incent.append(p_ybp - (p_cap + p_xbp * u))

    def insert_u_after_p_bp(self, u_xbp, u_ybp, p, p_cap, u_cap):

        self.xp_array_incent.append(u_xbp)
        if p_cap == 0:
            self.yp_array_incent.append(u_ybp - (p * u_ybp + u_cap))
        else:
            self.yp_array_incent.append(u_ybp - (p_cap + u_cap))

    def insert_p_after_u_bp(self, p_xbp, p_ybp, u, u_cap, p_cap):

        self.xp_array_incent.append(p_xbp)
        if u_cap == 0:
            self.yp_array_incent.append(p_ybp - (p_cap + u * p_xbp))
        else:
            self.yp_array_incent.append(p_ybp - (p_cap + u_cap))

    def setup_incentives(self):

        pv_incentives = dict()
        pv_incentives['federal'] = dict()
        pv_incentives['federal']['%'] = self.pv_itc_federal
        pv_incentives['federal']['%_max'] = self.pv_itc_federal_max
        pv_incentives['federal']['rebate'] = self.pv_rebate_federal
        pv_incentives['federal']['rebate_max'] = self.pv_rebate_federal_max
        pv_incentives['state'] = dict()
        pv_incentives['state']['%'] = self.pv_itc_state
        pv_incentives['state']['%_max'] = self.pv_itc_state_max
        pv_incentives['state']['rebate'] = self.pv_rebate_state
        pv_incentives['state']['rebate_max'] = self.pv_rebate_state_max
        pv_incentives['utility'] = dict()
        pv_incentives['utility']['%'] = self.pv_itc_utility
        pv_incentives['utility']['%_max'] = self.pv_itc_utility_max
        pv_incentives['utility']['rebate'] = self.pv_rebate_utility
        pv_incentives['utility']['rebate_max'] = self.pv_rebate_utility_max

        # Cost curve
        xp_array = [0, max_big_number]  # kW
        yp_array = [0, max_big_number * self.pv_cost]  # $

        # Apply incentives, initialize first value
        self.xp_array_incent = [0]
        self.yp_array_incent = [0]

        for region in pv_incentives.keys():

            # percentage based incentives
            p = pv_incentives[region]['%']
            p_cap = pv_incentives[region]['%_max']

            # rebates, for some reason called 'u' in REopt
            u = pv_incentives[region]['rebate']
            u_cap = pv_incentives[region]['rebate_max']

            # check discounts
            switch_percentage = False
            switch_rebate = False

            if p == 0 or p_cap == 0:
                switch_percentage = True
            if u == 0 or u_cap == 0:
                switch_rebate = True

            # start at second point, first is always zero
            for point in range(1, len(xp_array)):

                # previous points
                xp_prev = xp_array[point - 1]
                yp_prev = yp_array[point - 1]

                # current, unadjusted points
                xp = xp_array[point]
                yp = yp_array[point]

                # initialize the adjusted points on cost curve
                xa = xp
                ya = yp

                # initialize break points
                u_xbp = 0
                u_ybp = 0
                p_xbp = 0
                p_ybp = 0

                if not switch_rebate:
                    u_xbp = u_cap / u
                    u_ybp = slope(xp_prev, yp_prev, xp, yp) * u_xbp + intercept(xp_prev, yp_prev, xp, yp)

                if not switch_percentage:
                    p_xbp = (p_cap / p - intercept(xp_prev, yp_prev, xp, yp)) / slope(xp_prev, yp_prev, xp, yp)
                    p_ybp = p_cap / p
                if ((p * yp) < p_cap or p_cap == 0) and ((u * xp) < u_cap or u_cap == 0):
                    ya = yp - (p * yp + u * xp)
                elif (p * yp) < p_cap and (u * xp) >= u_cap:
                    if not switch_rebate:
                        if u * xp != u_cap:
                            self.insert_u_bp(u_xbp, u_ybp, p, u_cap)
                        switch_rebate = True
                    ya = yp - (p * yp + u_cap)
                elif (p * yp) >= p_cap and (u * xp) < u_cap:
                    if not switch_percentage:
                        if p * yp != p_cap:
                            self.insert_p_bp(p_xbp, p_ybp, u, p_cap)
                        switch_percentage = True
                    ya = yp - (p_cap + xp * u)
                elif p * yp >= p_cap and u * xp >= u_cap:
                    if not switch_rebate and not switch_percentage:
                        if p_xbp == u_xbp:
                            self.insert_u_bp(u_xbp, u_ybp, p, u_cap)
                            switch_percentage = True
                            switch_rebate = True
                        elif p_xbp < u_xbp:
                            if p * yp != p_cap:
                                self.insert_p_bp(p_xbp, p_ybp, u, p_cap)
                            switch_percentage = True
                            if u * xp != u_cap:
                                self.insert_u_after_p_bp(u_xbp, u_ybp, p, p_cap, u_cap)
                            switch_rebate = True
                        else:
                            if u * xp != u_cap:
                                self.insert_u_bp(u_xbp, u_ybp, p, u_cap)
                            switch_rebate = True
                            if p * yp != p_cap:
                                # insert p after u
                                self.insert_p_after_u_bp(p_xbp, p_ybp, u, u_cap, p_cap)
                            switch_percentage = True
                    elif switch_rebate and not switch_percentage:
                        if p * yp != p_cap:
                            self.insert_p_after_u_bp(p_xbp, p_ybp, u, u_cap, p_cap)
                        switch_percentage = True
                    elif switch_percentage and not switch_rebate:
                        if u * xp != u_cap:
                            self.insert_u_after_p_bp(u_xbp, u_ybp, p, p_cap, u_cap)
                        switch_rebate = True

                    # Finally compute adjusted values
                    if p_cap == 0:
                        ya = yp - (p * yp + u_cap)
                    elif u_cap == 0:
                        ya = yp - (p_cap + u * xp)
                    else:
                        ya = yp - (p_cap + u_cap)

                self.xp_array_incent.append(xa)
                self.yp_array_incent.append(ya)

        # clean up any duplicates
        for i in range(1, len(self.xp_array_incent)):
            if self.xp_array_incent[i] == self.xp_array_incent[i - 1]:
                self.xp_array_incent = self.xp_array_incent[0:i]
                self.yp_array_incent = self.yp_array_incent[0:i]
                break

        self.cap_cost_x = self.xp_array_incent
        for seg in range(1, len(self.xp_array_incent)):
            self.cap_cost_slope.append(round((self.yp_array_incent[seg] - self.yp_array_incent[seg - 1])/ self.xp_array_incent[seg] - self.xp_array_incent[seg - 1], 0))
            self.cap_cost_yint.append(round(self.yp_array_incent[seg] - self.cap_cost_slope[-1] * self.xp_array_incent[seg], 0))
        self.cap_cost_segments = len(self.cap_cost_slope)

        cap_cost_slope = list()
        cap_cost_x = list()
        cap_cost_yint = list()

        techs = self.techs
        if self.business_as_usual:
            techs = self.techs_bau

        for tech in techs:
            for seg in range(0, self.cap_cost_segments):
                if tech == 'PV' or tech == 'PVNM':
                    cap_cost_slope.append(self.cap_cost_slope[seg])
                    cap_cost_yint.append(self.cap_cost_yint[seg])
                else:
                    cap_cost_slope.append(0)
                    cap_cost_yint.append(0)
            for seg in range(0, self.cap_cost_segments + 1):
                if tech == 'PV' or tech == 'PVNM':
                    cap_cost_x.append(self.cap_cost_x[seg])
                else:
                    x = 0
                    if len(cap_cost_x) > 0 and cap_cost_x[-1] == 0:
                        x = max_big_number
                    cap_cost_x.append(x)

        self.output_args["CapCostSlope"] = cap_cost_slope
        self.output_args["CapCostX"] = cap_cost_x
        self.output_args["CapCostYInt"] = cap_cost_yint

        """
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
        """
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

        if "ProdIncentRate" not in self.output_args:
            prod_incent_array = self.tech_size * self.bin_size * [0]
        else:
            prod_incent_array = self.output_args["ProdIncentRate"]

        if "MaxProdIncent" not in self.output_args:
            max_prod_array = self.tech_size * [0]
        else:
            max_prod_array = self.output_args["MaxProdIncent"]

        if "MaxSizeForProdIncent" not in self.output_args:
            max_size_array = self.tech_size * [0]
        else:
            max_size_array = self.output_args["MaxSizeForProdIncent"]

        for i in range(tech * self.bin_size, (tech + 1) * self.bin_size):
            prod_incent_array[i] = prod_incent_rate

        max_prod_array[tech] = max_prod_incent
        max_size_array[tech] = max_size_for_prod_incent

        self.output_args["pwf_prod_incent"] = pwf_prod_incent
        self.output_args["ProdIncentRate"] = prod_incent_array
        self.output_args["MaxProdIncent"] = max_prod_array
        self.output_args["MaxSizeForProdIncent"] = max_size_array

    def setup_business_as_usual(self):
        if self.business_as_usual:

            self.output_args['CapCostSlope'] = self.tech_size_bau * [0]
            self.output_args['LevelizationFactor'] = self.tech_size_bau * [1.0]
            self.output_args['OMperUnitSize'] = self.tech_size_bau * [0]

            self.output_args['ProdIncentRate'] = self.bin_size * self.tech_size_bau * [0]
            self.output_args['MaxProdIncent'] = self.tech_size_bau * [0]
            self.output_args['MaxSizeForProdIncent'] = self.tech_size_bau * [0]

    def output_economics(self):

        args = self.output_args
        key = args.iterkeys()
        value = args.itervalues()
        for _ in range(len(args)):
            try:
                k = key.next()
                v = value.next()
                write_single_variable(self.out_name, v, k, 'a')
            except:
                log('ERROR', 'Error writing economics for ' + key)


