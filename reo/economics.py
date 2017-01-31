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

    owner_discount_rate_nominal = 0
    offtaker_discount_rate_nominal = 0
    rate_escalation_nominal = 0

    output_args = {}
    incentives = {}

    def __init__(self,econ_inputs,file_path='economics.dat', business_as_usual=False):

        self.out_name = file_path
        self.business_as_usual = business_as_usual


        econ_list = inputs(filter="economics")
        for k in econ_list.keys():
            setattr(self, k, econ_inputs.get(k))

        if self.macrs_years == 5:
            self.macrs_schedule = [0.2, 0.32, 0.192, 0.1152, 0.1152, 0.0576]  # IRS pub 946
        else:
            self.macrs_schedule = [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446]  # IRS pub 946


        self.prepare_economics()
        self.output_economics()

    def prepare_economics(self):

        self.offtaker_discount_rate_nominal = (1 + self.offtaker_discount_rate) * (1 + self.rate_inflation) - 1
        self.owner_discount_rate_nominal = (1 + self.owner_discount_rate) * (1 + self.rate_inflation) - 1
        self.rate_escalation_nominal = (1 + self.rate_escalation) * (1 + self.rate_inflation) - 1

        args = {}
        args["pwf_owner"] = annuity(self.analysis_period, 0, self.owner_discount_rate)
        args["pwf_offtaker"] = annuity(self.analysis_period, 0, self.offtaker_discount_rate)
        args["pwf_om"] = annuity(self.analysis_period, self.rate_inflation, self.owner_discount_rate_nominal)
        args["pwf_e"] = annuity(self.analysis_period, self.rate_escalation_nominal, self.offtaker_discount_rate_nominal)
        args["pwf_op"] = annuity(self.analysis_period, self.rate_escalation_nominal, self.owner_discount_rate_nominal)
        args["r_tax_offtaker"] = self.offtaker_tax_rate
        args["r_tax_owner"] = self.owner_tax_rate

        args["LevelizationFactor"] = round(
            annuity_degr(self.analysis_period, self.rate_escalation, self.offtaker_discount_rate, -self.rate_degradation) / args["pwf_e"], 5)
        # args["OMperUnitSize"]   = round(pv_OM * args["pwf_om"], 5)
        args["OMperUnitSize"] = self.pv_om

        incentives = {}
        incentives["ProdIncentRate"] = 12 * [0]
        incentives["MaxProdIncent"] = [0, 0, 0]
        incentives["MaxSizeForProdIncent"] = [0, 0, 0]

        ''' effective PV and battery prices with ITC and depreciation
            NOTES: (i) depreciation tax shields are inherently nominal --> no need to account for inflation
                  (ii) ITC and bonus depreciation are taken at end of year 1
        '''
        # Sunlamp base case: take ITC, bonus and macrs depreciation
        if self.flag_itc == 1 and self.flag_macrs == 1 and self.flag_bonus == 1:
            pv_tax_shield = batt_kW_tax_shield = batt_kWh_tax_shield = 0

            basis_pv = self.pv_cost * (1 - self.macrs_itc_reduction * self.rate_itc)
            basis_batt_kW = self.batt_cost_kw * (1 - self.macrs_itc_reduction * self.rate_itc)
            basis_batt_kWh = self.batt_cost_kwh * (1 - self.macrs_itc_reduction * self.rate_itc)

            bonus_pv = basis_pv * self.bonus_fraction * self.owner_tax_rate
            bonus_batt_kW = basis_batt_kW * self.bonus_fraction * self.owner_tax_rate
            bonus_batt_kWh = basis_batt_kWh * self.bonus_fraction * self.owner_tax_rate

            macr_base_pv = basis_pv * (1 - self.bonus_fraction)
            macr_base_batt_kW = basis_batt_kW * (1 - self.bonus_fraction)
            macr_base_batt_kWh = basis_batt_kWh * (1 - self.bonus_fraction)

            for idx, r in enumerate(self.macrs_schedule):  # tax shields are discounted to year zero
                pv_tax_shield += r * macr_base_pv * self.owner_tax_rate / (1 + self.owner_discount_rate_nominal) ** (idx + 1)
                batt_kW_tax_shield += r * macr_base_batt_kW * self.owner_tax_rate / (1 + self.owner_discount_rate_nominal) ** (idx + 1)
                batt_kWh_tax_shield += r * macr_base_batt_kWh * self.owner_tax_rate / (1 + self.owner_discount_rate_nominal) ** (idx + 1)

            # cost = price - federal tax benefits, where ITC and bonus are discounted 1 year using r_owner
            args["CapCostSlope"] = round(
                self.pv_cost - pv_tax_shield - self.rate_itc * self.pv_cost / (1 + self.owner_discount_rate_nominal) \
                - bonus_pv / (1 + self.owner_discount_rate_nominal), 4)
            args["StorageCostPerKW"] = round(
                self.batt_cost_kw - batt_kW_tax_shield - self.rate_itc * self.batt_cost_kw / (1 + self.owner_discount_rate_nominal) \
                - bonus_batt_kW / (1 + self.owner_discount_rate_nominal), 4)

            args["StorageCostPerKWH"] = round(
                self.batt_cost_kwh - batt_kWh_tax_shield - self.rate_itc * self.batt_cost_kwh / (1 + self.owner_discount_rate_nominal) \
                - bonus_batt_kWh / (1 + self.owner_discount_rate_nominal), 4)

        elif self.flag_itc == 0 and self.flag_macrs == 0:
            # cost = price
            args["CapCostSlope"] = round(self.pv_cost, 4)
            args["StorageCostPerKW"] = round(self.batt_cost_kw, 4)
            args["StorageCostPerKWH"] = round(self.batt_cost_kwh, 4)

        elif self.flag_itc == 1 and self.flag_macrs == 0:
            # cost = price - federal tax benefits, where ITC is discounted 1 year using r_owner
            args["CapCostSlope"] = round(self.pv_cost - self.rate_itc * self.pv_cost / (1 + self.owner_discount_rate_nominal), 4)
            args["StorageCostPerKW"] = round(
                self.batt_cost_kw - self.rate_itc * self.batt_cost_kw / (1 + self.owner_discount_rate_nominal), 4)
            args["StorageCostPerKWH"] = round(
                self.batt_cost_kwh - self.rate_itc * self.batt_cost_kwh / (1 + self.owner_discount_rate_nominal), 4)

        elif self.flag_itc == 1 and self.flag_macrs == 1 and self.flag_bonus == 0:
            pv_tax_shield = batt_kW_tax_shield = batt_kWh_tax_shield = 0

            macr_base_pv = self.pv_cost - self.macrs_itc_reduction * self.rate_itc * self.pv_cost
            macr_base_batt_kW = self.batt_cost_kw - self.macrs_itc_reduction * self.rate_itc * self.batt_cost_kw
            macr_base_batt_kWh = self.batt_cost_kwh - self.macrs_itc_reduction * self.rate_itc * self.batt_cost_kwh

            for idx, r in enumerate(self.macrs_schedule):  # tax shields are discounted to year zero
                pv_tax_shield += r * macr_base_pv * self.owner_tax_rate / (1 + self.owner_discount_rate_nominal) ** (idx + 1)
                batt_kW_tax_shield += r * macr_base_batt_kW * self.owner_tax_rate / (1 + self.owner_discount_rate_nominal) ** (idx + 1)
                batt_kWh_tax_shield += r * macr_base_batt_kWh * self.owner_tax_rate / (1 + self.owner_discount_rate_nominal) ** (idx + 1)

            # cost = price - federal tax benefits, where ITC is discounted 1 year using r_owner
            args["CapCostSlope"] = round(
                self.pv_cost - self.rate_itc * self.pv_cost / (1 + self.owner_discount_rate_nominal) - pv_tax_shield, 4)
            args["StorageCostPerKW"] = round(
                self.batt_cost_kw - self.rate_itc * self.batt_cost_kw / (1 + self.owner_discount_rate_nominal) - batt_kW_tax_shield, 4)
            args["StorageCostPerKWH"] = round(
                self.batt_cost_kwh - self.rate_itc * self.batt_cost_kwh / (1 + self.owner_discount_rate_nominal) - batt_kWh_tax_shield, 4)

        elif self.flag_itc == 0 and self.flag_macrs == 1 and self.flag_bonus == 0:
            pv_tax_shield = batt_kW_tax_shield = batt_kWh_tax_shield = 0

            for idx, r in enumerate(self.macrs_schedule):  # tax shields are discounted to year zero
                pv_tax_shield += r * self.pv_cost * self.owner_tax_rate / (1 + self.owner_discount_rate_nominal) ** (idx + 1)
                batt_kW_tax_shield += r * self.batt_cost_kw * self.owner_tax_rate / (1 + self.owner_discount_rate_nominal) ** (idx + 1)
                batt_kWh_tax_shield += r * self.batt_cost_kwh * self.owner_tax_rate / (1 + self.owner_discount_rate_nominal) ** (idx + 1)

            # cost = price - federal tax benefits
            args["CapCostSlope"] = round(self.pv_cost - pv_tax_shield, 4)
            args["StorageCostPerKW"] = round(self.batt_cost_kw - batt_kW_tax_shield, 4)
            args["StorageCostPerKWH"] = round(self.batt_cost_kwh - batt_kWh_tax_shield, 4)

        elif self.flag_itc == 0 and self.flag_macrs == 1 and self.flag_bonus == 1:
            pv_tax_shield = batt_kW_tax_shield = batt_kWh_tax_shield = 0

            bonus_pv = self.pv_cost * self.bonus_fraction * self.owner_tax_rate
            bonus_batt_kW = self.batt_cost_kw * self.bonus_fraction * self.owner_tax_rate
            bonus_batt_kWh = self.batt_cost_kwh * self.bonus_fraction * self.owner_tax_rate

            macr_base_pv = self.pv_cost * (1 - self.bonus_fraction)
            macr_base_batt_kW = self.batt_cost_kw * (1 - self.bonus_fraction)
            macr_base_batt_kWh = self.batt_cost_kwh * (1 - self.bonus_fraction)

            for idx, r in enumerate(self.macrs_schedule):  # tax shields are discounted to year zero
                pv_tax_shield += r * macr_base_pv * self.owner_tax_rate / (1 + self.owner_discount_rate_nominal) ** (idx + 1)
                batt_kW_tax_shield += r * macr_base_batt_kW * self.owner_tax_rate / (1 + self.owner_discount_rate_nominal) ** (idx + 1)
                batt_kWh_tax_shield += r * macr_base_batt_kWh * self.owner_tax_rate / (1 + self.owner_discount_rate_nominal) ** (idx + 1)

            # cost = price - federal tax benefits, where bonus is discounted 1 year using r_owner
            args["CapCostSlope"] = round(self.pv_cost - pv_tax_shield - bonus_pv / (1 + self.owner_discount_rate_nominal), 4)
            args["StorageCostPerKW"] = round(
                self.batt_cost_kw - batt_kW_tax_shield - bonus_batt_kW / (1 + self.owner_discount_rate_nominal), 4)
            args["StorageCostPerKWH"] = round(
                self.batt_cost_kwh - batt_kWh_tax_shield - bonus_batt_kWh / (1 + self.owner_discount_rate_nominal), 4)

        else:
            print 'ERROR: invalid combination of flags'

        '''battery replacement cost: one time capex in user defined year
            discounted back to t=0 with r_owner
        '''
        if self.flag_replace_batt == 1:
            args["StorageCostPerKW"] += round(self.batt_replacement_cost_kw / (1 + self.owner_discount_rate_nominal) ** self.batt_replacement_year, 4)
            args["StorageCostPerKWH"] += round(self.batt_replacement_cost_kwh / (1 + self.owner_discount_rate_nominal) ** self.batt_replacement_year, 4)

        if self.business_as_usual:
            args['CapCostSlope'] = 0
            args['LevelizationFactor'] = 1.0
            args['OMperUnitSize'] = 0
            incentives['ProdIncentRate'] = 4 * [0]
            incentives['MaxProdIncent'] = [0]
            incentives['MaxSizeForProdIncent'] = [0]

        self.output_args = args
        self.incentives = incentives

    def output_economics(self):

        args = self.output_args
        incentives = self.incentives

        # write new file
        key = args.iterkeys()
        value = args.itervalues()
        incent_name = incentives.iterkeys()
        incent_vals = incentives.itervalues()

        with open(self.out_name, 'w') as f:
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
            for _ in range(len(incentives)):
                try:
                    k = incent_name.next();
                    vals = incent_vals.next()
                    f.write(k + ': [\n')
                    for v in vals:
                        f.write(str(v) + ',\n')
                    f.write(']\n')
                except:
                    print '\033[91merror writing incentives\033[0m'
