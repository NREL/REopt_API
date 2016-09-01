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

    out_name = 'economics.dat'

    # flags
    flag_macrs = 1  # 0 == do not depreciate
    flag_ITC = 1  # 0 == do not take ITC
    flag_bonus = 1  # 0 == no bonus depreciation
    flag_replace_batt = 1  # 0 == no battery replacement

    # inputs
    analysis_period = 25  # years of analysis
    rate_inflation = 0.02  # percent/year inflation
    rate_offtaker = 0.08  # offtaker discount rate
    rate_owner = 0.08  # owner discount rate - set equal to r_offtaker for single party
    rate_escalation = 0.0039  # percent/year electricity escalation rate
    rate_tax = 0.35  # tax rate

    rate_itc = 0.30  # for both PV and storage
    macrs_yrs = 5  # 5 or 7 year shedules, taken for both PV and storage
    macrs_itc_reduction = 0.5  # if ITC is taken with macrs, the depreciable value is reduced by this fraction of the ITC
    bonus_fraction = 0.5  # this fraction of the depreciable value is taken in year 1 in addition to MACRS

    pv_cost = 2160  # nominal price in $/kW
    pv_om = 20  # $/kW/year
    rate_degradation = 0.005  # 0.5% annual degradation for solar panels, accounted for in LevelizationFactor
    batt_cost_kw = 1600  # nominal price in $/kW (inverter)
    batt_cost_kwh = 500  # nominal price in $/kWh
    batt_replacement_year = 10  # year in which battery is replaced
    batt_replacement_cost_kw = 200  # $/kW to replace battery inverter
    batt_replacement_cost_kwh = 200  # $/kWh to replace battery

    macrs_schedule = []
    output_args = {}
    incentives = {}

    def __init__(self, out_name, flag_macrs, flag_itc, flag_bonus, flag_replace_batt, analysis_period, rate_inflation,
                 rate_offtaker, rate_owner, rate_escalation, rate_tax, rate_itc, macrs_yrs, macrs_itc_reduction,
                 bonus_fraction, pv_price, pv_om, annual_degradation, batt_cost_kw, batt_cost_kwh, batt_replacement_year,
                 batt_replacement_cost_kw, batt_replacement_cost_kwh):

        if out_name is not None:
            self.out_name = out_name
        if flag_macrs is not None:
            self.flag_macrs = flag_macrs
        if flag_itc is not None:
            self.flag_ITC = flag_itc
        if flag_bonus is not None:
            self.flag_bonus = flag_bonus
        if flag_replace_batt is not None:
            self.flag_replace_batt = flag_replace_batt
        if analysis_period is not None:
            self.analysis_period = analysis_period
        if rate_inflation is not None:
            self.rate_inflation = rate_inflation
        if rate_offtaker is not None:
            self.rate_offtaker = rate_offtaker
        if rate_owner is not None:
            self.rate_owner = rate_owner
        if rate_escalation is not None:
            self.rate_escalation = rate_escalation
        if rate_tax is not None:
            self.rate_tax = rate_tax
        if rate_itc is not None:
            self.rate_itc = rate_itc
        if macrs_yrs is not None:
            self.macrs_yrs = macrs_yrs
        if macrs_itc_reduction is not None:
            self.macrs_itc_reduction = macrs_itc_reduction
        if bonus_fraction is not None:
            self.bonus_fraction = bonus_fraction
        if pv_price is not None:
            self.pv_cost = pv_price
        if pv_om is not None:
            self.pv_om = pv_om
        if annual_degradation is not None:
            self.rate_degradation = annual_degradation
        if batt_cost_kw is not None:
            self.batt_cost_kw = batt_cost_kw
        if batt_cost_kwh is not None:
            self.batt_cost_kwh = batt_cost_kwh
        if batt_replacement_year is not None:
            self.batt_replacement_year = batt_replacement_year
        if batt_replacement_cost_kw is not None:
            self.batt_replacement_cost_kw = batt_replacement_cost_kw
        if batt_replacement_cost_kwh is not None:
            self.batt_replacement_cost_kwh = batt_replacement_cost_kwh

        if self.macrs_yrs == 5:
            self.macrs_schedule = [0.2, 0.32, 0.192, 0.1152, 0.1152, 0.0576]  # IRS pub 946
        else:
            self.macrs_schedule = [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446]  # IRS pub 946

        self.prepare_economics()
        self.output_economics()

    def prepare_economics(self):

        args = {}
        args["pwf_owner"] = annuity(self.analysis_period, 0, self.rate_owner)
        args["pwf_offtaker"] = annuity(self.analysis_period, 0, self.rate_offtaker)
        args["pwf_om"] = annuity(self.analysis_period, self.rate_inflation, self.rate_owner)
        args["pwf_e"] = annuity(self.analysis_period, self.rate_escalation, self.rate_offtaker)
        args["pwf_op"] = annuity(self.analysis_period, self.rate_escalation, self.rate_owner)

        args["LevelizationFactor"] = round(
            annuity_degr(self.analysis_period, self.rate_escalation, self.rate_offtaker, -self.rate_degradation) / args["pwf_e"], 5)
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
        if self.flag_ITC == 1 and self.flag_macrs == 1 and self.flag_bonus == 1:
            pv_tax_shield = batt_kW_tax_shield = batt_kWh_tax_shield = 0

            basis_pv = self.pv_cost * (1 - self.macrs_itc_reduction * self.rate_itc)
            basis_batt_kW = self.batt_cost_kw * (1 - self.macrs_itc_reduction * self.rate_itc)
            basis_batt_kWh = self.batt_cost_kwh * (1 - self.macrs_itc_reduction * self.rate_itc)

            bonus_pv = basis_pv * self.bonus_fraction * self.rate_tax
            bonus_batt_kW = basis_batt_kW * self.bonus_fraction * self.rate_tax
            bonus_batt_kWh = basis_batt_kWh * self.bonus_fraction * self.rate_tax

            macr_base_pv = basis_pv * (1 - self.bonus_fraction)
            macr_base_batt_kW = basis_batt_kW * (1 - self.bonus_fraction)
            macr_base_batt_kWh = basis_batt_kWh * (1 - self.bonus_fraction)

            for idx, r in enumerate(self.macrs_schedule):  # tax shields are discounted to year zero
                pv_tax_shield += r * macr_base_pv * self.rate_tax / (1 + self.rate_owner) ** (idx + 1)
                batt_kW_tax_shield += r * macr_base_batt_kW * self.rate_tax / (1 + self.rate_owner) ** (idx + 1)
                batt_kWh_tax_shield += r * macr_base_batt_kWh * self.rate_tax / (1 + self.rate_owner) ** (idx + 1)

            # cost = price - federal tax benefits, where ITC and bonus are discounted 1 year using r_owner
            args["CapCostSlope"] = round(
                self.pv_cost - pv_tax_shield - self.rate_itc * self.pv_cost / (1 + self.rate_owner) \
                - bonus_pv / (1 + self.rate_owner), 4)
            args["StorageCostPerKW"] = round(
                self.batt_cost_kw - batt_kW_tax_shield - self.rate_itc * self.batt_cost_kw / (1 + self.rate_owner) \
                - bonus_batt_kW / (1 + self.rate_owner), 4)

            args["StorageCostPerKWH"] = round(
                self.batt_cost_kwh - batt_kWh_tax_shield - self.rate_itc * self.batt_cost_kwh / (1 + self.rate_owner) \
                - bonus_batt_kWh / (1 + self.rate_owner), 4)

        elif self.flag_ITC == 0 and self.flag_macrs == 0:
            # cost = price
            args["CapCostSlope"] = round(self.pv_cost, 4)
            args["StorageCostPerKW"] = round(self.batt_cost_kw, 4)
            args["StorageCostPerKWH"] = round(self.batt_cost_kwh, 4)

        elif self.flag_ITC == 1 and self.flag_macrs == 0:
            # cost = price - federal tax benefits, where ITC is discounted 1 year using r_owner
            args["CapCostSlope"] = round(self.pv_cost - self.rate_itc * self.pv_cost / (1 + self.rate_owner), 4)
            args["StorageCostPerKW"] = round(
                self.batt_cost_kw - self.rate_itc * self.batt_cost_kw / (1 + self.rate_owner), 4)
            args["StorageCostPerKWH"] = round(
                self.batt_cost_kwh - self.rate_itc * self.batt_cost_kwh / (1 + self.rate_owner), 4)

        elif self.flag_ITC == 1 and self.flag_macrs == 1 and self.flag_bonus == 0:
            pv_tax_shield = batt_kW_tax_shield = batt_kWh_tax_shield = 0

            macr_base_pv = self.pv_cost - self.macrs_itc_reduction * self.rate_itc * self.pv_cost
            macr_base_batt_kW = self.batt_cost_kw - self.macrs_itc_reduction * self.rate_itc * self.batt_cost_kw
            macr_base_batt_kWh = self.batt_cost_kwh - self.macrs_itc_reduction * self.rate_itc * self.batt_cost_kwh

            for idx, r in enumerate(self.macrs_schedule):  # tax shields are discounted to year zero
                pv_tax_shield += r * macr_base_pv * self.rate_tax / (1 + self.rate_owner) ** (idx + 1)
                batt_kW_tax_shield += r * macr_base_batt_kW * self.rate_tax / (1 + self.rate_owner) ** (idx + 1)
                batt_kWh_tax_shield += r * macr_base_batt_kWh * self.rate_tax / (1 + self.rate_owner) ** (idx + 1)

            # cost = price - federal tax benefits, where ITC is discounted 1 year using r_owner
            args["CapCostSlope"] = round(
                self.pv_cost - self.rate_itc * self.pv_cost / (1 + self.rate_owner) - pv_tax_shield, 4)
            args["StorageCostPerKW"] = round(
                self.batt_cost_kw - self.rate_itc * self.batt_cost_kw / (1 + self.rate_owner) - batt_kW_tax_shield, 4)
            args["StorageCostPerKWH"] = round(
                self.batt_cost_kwh - self.rate_itc * self.batt_cost_kwh / (1 + self.rate_owner) - batt_kWh_tax_shield, 4)

        elif self.flag_ITC == 0 and self.flag_macrs == 1 and self.flag_bonus == 0:
            pv_tax_shield = batt_kW_tax_shield = batt_kWh_tax_shield = 0

            for idx, r in enumerate(self.macrs_schedule):  # tax shields are discounted to year zero
                pv_tax_shield += r * self.pv_cost * self.rate_tax / (1 + self.rate_owner) ** (idx + 1)
                batt_kW_tax_shield += r * self.batt_cost_kw * self.rate_tax / (1 + self.rate_owner) ** (idx + 1)
                batt_kWh_tax_shield += r * self.batt_cost_kwh * self.rate_tax / (1 + self.rate_owner) ** (idx + 1)

            # cost = price - federal tax benefits
            args["CapCostSlope"] = round(self.pv_cost - pv_tax_shield, 4)
            args["StorageCostPerKW"] = round(self.batt_cost_kw - batt_kW_tax_shield, 4)
            args["StorageCostPerKWH"] = round(self.batt_cost_kwh - batt_kWh_tax_shield, 4)

        elif self.flag_ITC == 0 and self.flag_macrs == 1 and self.flag_bonus == 1:
            pv_tax_shield = batt_kW_tax_shield = batt_kWh_tax_shield = 0

            bonus_pv = self.pv_cost * self.bonus_fraction * self.rate_tax
            bonus_batt_kW = self.batt_cost_kw * self.bonus_fraction * self.rate_tax
            bonus_batt_kWh = self.batt_cost_kwh * self.bonus_fraction * self.rate_tax

            macr_base_pv = self.pv_cost * (1 - self.bonus_fraction)
            macr_base_batt_kW = self.batt_cost_kw * (1 - self.bonus_fraction)
            macr_base_batt_kWh = self.batt_cost_kwh * (1 - self.bonus_fraction)

            for idx, r in enumerate(self.macrs_schedule):  # tax shields are discounted to year zero
                pv_tax_shield += r * macr_base_pv * self.rate_tax / (1 + self.rate_owner) ** (idx + 1)
                batt_kW_tax_shield += r * macr_base_batt_kW * self.rate_tax / (1 + self.rate_owner) ** (idx + 1)
                batt_kWh_tax_shield += r * macr_base_batt_kWh * self.rate_tax / (1 + self.rate_owner) ** (idx + 1)

            # cost = price - federal tax benefits, where bonus is discounted 1 year using r_owner
            args["CapCostSlope"] = round(self.pv_cost - pv_tax_shield - bonus_pv / (1 + self.rate_owner), 4)
            args["StorageCostPerKW"] = round(
                self.batt_cost_kw - batt_kW_tax_shield - bonus_batt_kW / (1 + self.rate_owner), 4)
            args["StorageCostPerKWH"] = round(
                self.batt_cost_kwh - batt_kWh_tax_shield - bonus_batt_kWh / (1 + self.rate_owner), 4)

        else:
            print 'ERROR: invalid combination of flags'

        '''battery replacement cost: one time capex in user defined year
            discounted back to t=0 with r_owner
        '''
        if self.flag_replace_batt == 1:
            args["StorageCostPerKW"] += round(self.batt_replacement_cost_kw / (1 + self.rate_owner) ** self.batt_replacement_year, 4)
            args["StorageCostPerKWH"] += round(self.batt_replacement_cost_kwh / (1 + self.rate_owner) ** self.batt_replacement_year, 4)

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
                    k = key.next();
                    v = value.next()
                    f.write(k + ': [\n')
                    f.write(str(v) + ',\n')
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
