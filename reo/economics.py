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

def annuity(y, esc, disc):
    '''this formulation assumes cost growth in first period
        i.e. it is a geometric sum of (1+esc)^n / (1+disc)^n
        for n = 1,..., y
    '''
    if esc != disc:
        x = (1 + esc) / (1 + disc)
        pwf = round(x * (1 - x ** y) / (1 - x), 5)
    else:
        pwf = y
    return pwf


def annuity_degr(yrs, esc, disc, degradation):
    '''
    same as VBA Function PWaDegr(
    :param y: years
    :param esc: escalation rate
    :param disc: discount rate
    :param degradation: annual degradation
    :return: present worth factor with degradation
    '''
    pwf = 0
    for yr in range(1, yrs + 1):
        pwf += (1 + esc) ** yr / (1 + disc) ** yr * (1 + degradation) ** (yr - 1)
    return pwf


class Economics:

    out_name = 'economics.dat'

    # flags
    flag_macrs = 1  # 0 == do not depreciate
    flag_ITC = 1  # 0 == do not take ITC
    flag_bonus = 1  # 0 == no bonus depreciation
    flag_replace_batt = 1  # 0 == no battery replacement

    # inputs
    y = 25  # years of analysis
    i = 0.02  # percent/year inflation
    r_offtaker = 0.08  # offtaker discount rate
    r_owner = 0.08  # owner discount rate - set equal to r_offtaker for single party
    EscE = 0.0039  # percent/year electricity escalation rate
    tax_rate = 0.35  # tax rate

    ITC_rate = 0.30  # for both PV and storage
    macrs_yrs = 5  # 5 or 7 year shedules, taken for both PV and storage
    macrsITC_reduction = 0.5  # if ITC is taken with macrs, the depreciable value is reduced by this fraction of the ITC
    bonus_fraction = 0.5  # this fraction of the depreciable value is taken in year 1 in addition to MACRS

    pv_price = 2160  # nominal price in $/kW
    pv_OM = 20  # $/kW/year
    annualDegrade = 0.005  # 0.5% annual degradation for solar panels, accounted for in LevelizationFactor
    batt_price_kW = 1600  # nominal price in $/kW (inverter)
    batt_price_kWh = 500  # nominal price in $/kWh
    batt_repl_yr = 10  # year in which battery is replaced
    batt_repl_kW = 200  # $/kW to replace battery inverter
    batt_repl_kWh = 200  # $/kWh to replace battery

    macrs_schedule = []
    output_args = {}
    incentives = {}

    def __init__(self, out_name, flag_macrs, flag_ITC, flag_bonus, flag_replace_batt, analysis_period, r_inflation,
                 r_offtaker, r_owner, r_escalation, r_tax, r_ITC, macrs_yrs, macrsITC_reduction, bonus_fraction,
                 pv_price, pv_OM, annual_degradation, batt_price_kW, batt_price_kWh, batt_replacement_year,
                 batt_replacement_kW, batt_replacement_kWh):

        if out_name is not None:
            self.out_name = out_name
        if flag_macrs is not None:
            self.flag_macrs = flag_macrs
        if flag_ITC is not None:
            self.flag_ITC = flag_ITC
        if analysis_period is not None:
            self.y = analysis_period
        if r_inflation is not None:
            self.i = r_inflation
        if r_offtaker is not None:
            self.r_offtaker = r_offtaker
        if r_owner is not None:
            self.r_owner = r_owner
        if r_escalation is not None:
            self.EscE = r_escalation
        if r_tax is not None:
            self.tax_rate = r_tax
        if r_ITC is not None:
            self.ITC_rate = r_ITC
        if macrs_yrs is not None:
            self.macrs_yrs = macrs_yrs
        if macrsITC_reduction is not None:
            self.macrsITC_reduction = macrsITC_reduction
        if bonus_fraction is not None:
            self.bonus_fraction = bonus_fraction
        if pv_price is not None:
            self.pv_price = pv_price
        if pv_OM is not None:
            self.pv_OM = pv_OM
        if annual_degradation is not None:
            self.annualDegrade = annual_degradation
        if batt_price_kW is not None:
            self.batt_price_kW = batt_price_kW
        if batt_price_kWh is not None:
            self.batt_price_kWh = batt_price_kWh
        if batt_replacement_year is not None:
            self.batt_repl_yr = batt_replacement_year
        if batt_replacement_kW is not None:
            self.batt_repl_kW = batt_replacement_kW
        if batt_replacement_kWh is not None:
            self.batt_repl_kWh = batt_replacement_kWh

        if self.macrs_yrs == 5:
            self.macrs_schedule = [0.2, 0.32, 0.192, 0.1152, 0.1152, 0.0576]  # IRS pub 946
        else:
            self.macrs_schedule = [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446]  # IRS pub 946

        self.prepare_economics()
        self.output_economics()

    def prepare_economics(self):

        args = {}
        args["pwf_owner"] = annuity(self.y, 0, self.r_owner)
        args["pwf_offtaker"] = annuity(self.y, 0, self.r_offtaker)
        args["pwf_om"] = annuity(self.y, self.i, self.r_owner)
        args["pwf_e"] = annuity(self.y, self.EscE, self.r_offtaker)
        args["pwf_op"] = annuity(self.y, self.EscE, self.r_owner)

        args["LevelizationFactor"] = round(
            annuity_degr(self.y, self.EscE, self.r_offtaker, -self.annualDegrade) / args["pwf_e"], 5)
        # args["OMperUnitSize"]   = round(pv_OM * args["pwf_om"], 5)
        args["OMperUnitSize"] = self.pv_OM

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

            basis_pv = self.pv_price * (1 - self.macrsITC_reduction * self.ITC_rate)
            basis_batt_kW = self.batt_price_kW * (1 - self.macrsITC_reduction * self.ITC_rate)
            basis_batt_kWh = self.batt_price_kWh * (1 - self.macrsITC_reduction * self.ITC_rate)

            bonus_pv = basis_pv * self.bonus_fraction * self.tax_rate
            bonus_batt_kW = basis_batt_kW * self.bonus_fraction * self.tax_rate
            bonus_batt_kWh = basis_batt_kWh * self.bonus_fraction * self.tax_rate

            macr_base_pv = basis_pv * (1 - self.bonus_fraction)
            macr_base_batt_kW = basis_batt_kW * (1 - self.bonus_fraction)
            macr_base_batt_kWh = basis_batt_kWh * (1 - self.bonus_fraction)

            for idx, r in enumerate(self.macrs_schedule):  # tax shields are discounted to year zero
                pv_tax_shield += r * macr_base_pv * self.tax_rate / (1 + self.r_owner) ** (idx + 1)
                batt_kW_tax_shield += r * macr_base_batt_kW * self.tax_rate / (1 + self.r_owner) ** (idx + 1)
                batt_kWh_tax_shield += r * macr_base_batt_kWh * self.tax_rate / (1 + self.r_owner) ** (idx + 1)

            # cost = price - federal tax benefits, where ITC and bonus are discounted 1 year using r_owner
            args["CapCostSlope"] = round(
                self.pv_price - pv_tax_shield - self.ITC_rate * self.pv_price / (1 + self.r_owner) \
                - bonus_pv / (1 + self.r_owner), 4)
            args["StorageCostPerKW"] = round(
                self.batt_price_kW - batt_kW_tax_shield - self.ITC_rate * self.batt_price_kW / (1 + self.r_owner) \
                - bonus_batt_kW / (1 + self.r_owner), 4)

            args["StorageCostPerKWH"] = round(
                self.batt_price_kWh - batt_kWh_tax_shield - self.ITC_rate * self.batt_price_kWh / (1 + self.r_owner) \
                - bonus_batt_kWh / (1 + self.r_owner), 4)

        elif self.flag_ITC == 0 and self.flag_macrs == 0:
            # cost = price
            args["CapCostSlope"] = round(self.pv_price, 4)
            args["StorageCostPerKW"] = round(self.batt_price_kW, 4)
            args["StorageCostPerKWH"] = round(self.batt_price_kWh, 4)

        elif self.flag_ITC == 1 and self.flag_macrs == 0:
            # cost = price - federal tax benefits, where ITC is discounted 1 year using r_owner
            args["CapCostSlope"] = round(self.pv_price - self.ITC_rate * self.pv_price / (1 + self.r_owner), 4)
            args["StorageCostPerKW"] = round(
                self.batt_price_kW - self.ITC_rate * self.batt_price_kW / (1 + self.r_owner), 4)
            args["StorageCostPerKWH"] = round(
                self.batt_price_kWh - self.ITC_rate * self.batt_price_kWh / (1 + self.r_owner), 4)

        elif self.flag_ITC == 1 and self.flag_macrs == 1 and self.flag_bonus == 0:
            pv_tax_shield = batt_kW_tax_shield = batt_kWh_tax_shield = 0

            macr_base_pv = self.pv_price - self.macrsITC_reduction * self.ITC_rate * self.pv_price
            macr_base_batt_kW = self.batt_price_kW - self.macrsITC_reduction * self.ITC_rate * self.batt_price_kW
            macr_base_batt_kWh = self.batt_price_kWh - self.macrsITC_reduction * self.ITC_rate * self.batt_price_kWh

            for idx, r in enumerate(self.macrs_schedule):  # tax shields are discounted to year zero
                pv_tax_shield += r * macr_base_pv * self.tax_rate / (1 + self.r_owner) ** (idx + 1)
                batt_kW_tax_shield += r * macr_base_batt_kW * self.tax_rate / (1 + self.r_owner) ** (idx + 1)
                batt_kWh_tax_shield += r * macr_base_batt_kWh * self.tax_rate / (1 + self.r_owner) ** (idx + 1)

            # cost = price - federal tax benefits, where ITC is discounted 1 year using r_owner
            args["CapCostSlope"] = round(
                self.pv_price - self.ITC_rate * self.pv_price / (1 + self.r_owner) - pv_tax_shield, 4)
            args["StorageCostPerKW"] = round(
                self.batt_price_kW - self.ITC_rate * self.batt_price_kW / (1 + self.r_owner) - batt_kW_tax_shield, 4)
            args["StorageCostPerKWH"] = round(
                self.batt_price_kWh - self.ITC_rate * self.batt_price_kWh / (1 + self.r_owner) - batt_kWh_tax_shield, 4)

        elif self.flag_ITC == 0 and self.flag_macrs == 1 and self.flag_bonus == 0:
            pv_tax_shield = batt_kW_tax_shield = batt_kWh_tax_shield = 0

            for idx, r in enumerate(self.macrs_schedule):  # tax shields are discounted to year zero
                pv_tax_shield += r * self.pv_price * self.tax_rate / (1 + self.r_owner) ** (idx + 1)
                batt_kW_tax_shield += r * self.batt_price_kW * self.tax_rate / (1 + self.r_owner) ** (idx + 1)
                batt_kWh_tax_shield += r * self.batt_price_kWh * self.tax_rate / (1 + self.r_owner) ** (idx + 1)

            # cost = price - federal tax benefits
            args["CapCostSlope"] = round(self.pv_price - pv_tax_shield, 4)
            args["StorageCostPerKW"] = round(self.batt_price_kW - batt_kW_tax_shield, 4)
            args["StorageCostPerKWH"] = round(self.batt_price_kWh - batt_kWh_tax_shield, 4)

        elif self.flag_ITC == 0 and self.flag_macrs == 1 and self.flag_bonus == 1:
            pv_tax_shield = batt_kW_tax_shield = batt_kWh_tax_shield = 0

            bonus_pv = self.pv_price * self.bonus_fraction * self.tax_rate
            bonus_batt_kW = self.batt_price_kW * self.bonus_fraction * self.tax_rate
            bonus_batt_kWh = self.batt_price_kWh * self.bonus_fraction * self.tax_rate

            macr_base_pv = self.pv_price * (1 - self.bonus_fraction)
            macr_base_batt_kW = self.batt_price_kW * (1 - self.bonus_fraction)
            macr_base_batt_kWh = self.batt_price_kWh * (1 - self.bonus_fraction)

            for idx, r in enumerate(self.macrs_schedule):  # tax shields are discounted to year zero
                pv_tax_shield += r * macr_base_pv * self.tax_rate / (1 + self.r_owner) ** (idx + 1)
                batt_kW_tax_shield += r * macr_base_batt_kW * self.tax_rate / (1 + self.r_owner) ** (idx + 1)
                batt_kWh_tax_shield += r * macr_base_batt_kWh * self.tax_rate / (1 + self.r_owner) ** (idx + 1)

            # cost = price - federal tax benefits, where bonus is discounted 1 year using r_owner
            args["CapCostSlope"] = round(self.pv_price - pv_tax_shield - bonus_pv / (1 + self.r_owner), 4)
            args["StorageCostPerKW"] = round(
                self.batt_price_kW - batt_kW_tax_shield - bonus_batt_kW / (1 + self.r_owner), 4)
            args["StorageCostPerKWH"] = round(
                self.batt_price_kWh - batt_kWh_tax_shield - bonus_batt_kWh / (1 + self.r_owner), 4)

        else:
            print 'ERROR: invalid combination of flags'

        '''battery replacement cost: one time capex in user defined year
            discounted back to t=0 with r_owner
        '''
        if self.flag_replace_batt == 1:
            args["StorageCostPerKW"] += round(self.batt_repl_kW / (1 + self.r_owner) ** self.batt_repl_yr, 4)
            args["StorageCostPerKWH"] += round(self.batt_repl_kWh / (1 + self.r_owner) ** self.batt_repl_yr, 4)

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
