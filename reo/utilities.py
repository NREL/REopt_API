import os
from log_levels import log
from numpy import npv


def attribute_inputs(inputs):
    return {k:v for k,v in inputs.items() if k[0]==k[0].lower() and v is not None}

class API_Error:
    def __init__(self, e):
        # e is a caught Exception
        self.errors = {}
        if len(e.args) == 2:
            # arg 1 - filename where exception was thrown
            # arg 2 - custom error message
            error_type, messages = e
        else:
            # error was not thrown intentionally
            error_type, messages = 'Exception', e.args
            if hasattr(e, 'traceback'):
                self.errors["Traceback"] = e.traceback

        self.errors[error_type] = messages

    @property
    def response(self):
        return {"REopt": {"Error":self.errors}}

def check_directory_created(path):
    if not os.path.exists(path):
        log('ERROR', "Directory: " + path + " failed to create")
        raise RuntimeError('utilties', "Directory failed to create: " + path)

def slope(x1, y1, x2, y2):
    return (y2 - y1) / (x2 - x1)


def intercept(x1, y1, x2, y2):
    return y2 - slope(x1, y1, x2, y2) * x2


def annuity(analysis_period, rate_escalation, rate_discount):
    """
        this formulation assumes cost growth in first period
        i.e. it is a geometric sum of (1+rate_escalation)^n / (1+rate_discount)^n
        for n = 1,..., analysis_period
    """
    x = (1 + rate_escalation) / (1 + rate_discount)
    if x != 1:
        pwf = round(x * (1 - x ** analysis_period) / (1 - x), 5)
    else:
        pwf = analysis_period
    return pwf


def degradation_factor(analysis_period, rate_degradation):
    factor = 1
    factors = [factor]
    for yr in range(1, int(analysis_period)):
        factor *= (1 - rate_degradation)
        factors.append(factor)
    return sum(factors)/analysis_period


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
    for yr in range(1, int(analysis_period + 1)):
        pwf += (1 + rate_escalation) ** yr / (1 + rate_discount) ** yr * (1 + rate_degradation) ** (yr - 1)
    return pwf


def insert_u_bp(xp_array_incent, yp_array_incent, region, u_xbp, u_ybp, p, u_cap):

    xp_array_incent[region].append(u_xbp)
    yp_array_incent[region].append(u_ybp - u_ybp * p + u_cap)
    return xp_array_incent, yp_array_incent


def insert_p_bp(xp_array_incent, yp_array_incent, region, p_xbp, p_ybp, u, p_cap):

    xp_array_incent[region].append(p_xbp)
    yp_array_incent[region].append(p_ybp - (p_cap + p_xbp * u))
    return xp_array_incent, yp_array_incent


def insert_u_after_p_bp(xp_array_incent, yp_array_incent, region, u_xbp, u_ybp, p, p_cap, u_cap):

    xp_array_incent[region].append(u_xbp)
    if p_cap == 0:
        yp_array_incent[region].append(u_ybp - (p * u_ybp + u_cap))
    else:
        yp_array_incent[region].append(u_ybp - (p_cap + u_cap))
    return xp_array_incent, yp_array_incent


def insert_p_after_u_bp(xp_array_incent, yp_array_incent, region, p_xbp, p_ybp, u, u_cap, p_cap):

    xp_array_incent[region].append(p_xbp)
    if u_cap == 0:
        yp_array_incent[region].append(p_ybp - (p_cap + u * p_xbp))
    else:
        yp_array_incent[region].append(p_ybp - (p_cap + u_cap))
    return xp_array_incent, yp_array_incent


def setup_capital_cost_incentive(itc_basis, replacement_cost, replacement_year,
                                 discount_rate, tax_rate, itc,
                                 macrs_schedule, macrs_bonus_pct, macrs_itc_reduction):

    """ effective PV and battery prices with ITC and depreciation
        (i) depreciation tax shields are inherently nominal --> no need to account for inflation
        (ii) ITC and bonus depreciation are taken at end of year 1
        (iii) battery replacement cost: one time capex in user defined year discounted back to t=0 with r_owner
        (iv) Assume that cash incentives reduce ITC basis
        (v) Assume cash incentives are not taxable, (don't affect tax savings from MACRS)
        (vi) Cash incentives should be applied before this function into "itc_basis".
             This includes all rebates and percentage-based incentives besides the ITC
    """

    # itc reduces depreciable_basis
    depr_basis = itc_basis * (1 - macrs_itc_reduction * itc)

    # Bonus depreciation taken from tech cost after itc reduction ($/kW)
    bonus_depreciation = depr_basis * macrs_bonus_pct

    # Assume the ITC and bonus depreciation reduce the depreciable basis ($/kW)
    depr_basis -= bonus_depreciation

    # Calculate replacement cost, discounted to the replacement year accounting for tax deduction
    replacement = replacement_cost * (1-tax_rate) / ((1 + discount_rate) ** replacement_year)

    # Compute savings from depreciation and itc in array to capture NPV
    tax_savings_array = [0]
    for idx, macrs_rate in enumerate(macrs_schedule):
        depreciation_amount = macrs_rate * depr_basis
        taxable_income = depreciation_amount
        if idx == 0:
            depreciation_amount += bonus_depreciation
        taxable_income = depreciation_amount
        tax_savings_array.append(taxable_income * tax_rate)

    # Add the ITC to the tax savings
    tax_savings_array[1] += itc_basis * itc

    # Compute the net present value of the tax savings
    tax_savings = npv(discount_rate, tax_savings_array)

    # Adjust cost curve to account for itc and depreciation savings ($/kW)
    cap_cost_slope = itc_basis - tax_savings + replacement

    # Sanity check
    if cap_cost_slope < 0:
        cap_cost_slope = 0

    return round(cap_cost_slope, 4)
