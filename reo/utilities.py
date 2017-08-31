import os
from log_levels import log


class API_Error:
    def __init__(self, e):
        #e is a caught Exception
        self.errors = {}
        if len(e.args)==2:
            #arg 1 - filename where exception was thrown
            #arg 2 - custom error message
            error_type,messages = e
        else:
            #error was not thrown intentiallty in this code
            error_type,messages = 'Exception',e

        self.errors[error_type]= messages

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


def setup_capital_cost_incentive(tech_cost, replacement_cost, replacement_year,
                                 discount_rate, tax_rate, itc,
                                 macrs_schedule, macrs_bonus_fraction, macrs_itc_reduction):

    """ effective PV and battery prices with ITC and depreciation
        (i) depreciation tax shields are inherently nominal --> no need to account for inflation
        (ii) ITC and bonus depreciation are taken at end of year 1
        (iii) battery replacement cost: one time capex in user defined year discounted back to t=0 with r_owner
    """

    # Assume that cash incentives do not reduce ITC basis or depreciation basis ($/kW)
    depreciable_cash_incentives = 0

    # Amount of money the ITC can be applied against ($/kW)
    itc_basis = tech_cost - depreciable_cash_incentives

    # Assume the ITC reduces the depreciable basis ($/kW)
    macrs_basis = itc_basis * (1 - (1 - macrs_itc_reduction) * itc)

    # Compute depreciation amount before tax.  ($/kW)
    depreciation_amount = 0
    for idx, r in enumerate(macrs_schedule):
        rate = r
        if idx == 0:
            rate += macrs_bonus_fraction
        depreciation_amount += (rate * macrs_basis) / (1 + discount_rate) ** (idx + 1)

    # Compute the effective tax savings ($/kW)
    tax_savings = depreciation_amount * tax_rate

    # Adjust cost curve to account for itc and depreciation savings ($/kW)
    cap_cost_slope = tech_cost * (1 - itc) - tax_savings

    # Factor in any out year replacements
    cap_cost_slope += replacement_cost / (1 + discount_rate) ** replacement_year

    return round(cap_cost_slope, 4)
