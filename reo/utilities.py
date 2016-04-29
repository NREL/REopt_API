import numpy as np


def present_worth_factor(years, escalation_rate, discount_rate):
    pwf = 0
    for y in range(1, years+1):
        pwf = pwf + np.power(1+escalation_rate, y)/np.power(1+discount_rate, y)
    return np.around(pwf, 2)
