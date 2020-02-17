# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
#!usr/bin/python
import copy
from math import floor
import pandas as pd

class Generator():
    def __init__(self, diesel_kw, fuel_available, b, m, diesel_min_turndown):
        self.kw = diesel_kw
        self.fuel_available = fuel_available if (self.kw or 0) > 0 else 0
        self.b = b  # input b: fuel curve intercept
        self.m = m
        self.min_turndown = diesel_min_turndown
        self.genmin = self.min_turndown * self.kw

        if self.fuel_available == 1e9:
                self.fuel_available = 660

    def gen_avail(self, n_steps_per_hour):  # kW
        if self.fuel_available - self.b > 0:
            return min((self.fuel_available * n_steps_per_hour - self.b) / self.m, self.kw)
        else:
            return 0

    def fuel_consume(self, gen_output, n_steps_per_hour):  # kW
        if self.gen_avail(n_steps_per_hour) >= self.genmin and gen_output > 0:
            gen_output = max(self.genmin, min(gen_output, self.gen_avail(n_steps_per_hour)))
            fuel_consume = (self.b + self.m * gen_output) / n_steps_per_hour
            self.fuel_available -= min(self.fuel_available, fuel_consume)
        else:
            gen_output = 0
        return gen_output


class Battery():
    def __init__(self, batt_kwh, batt_kw, batt_roundtrip_efficiency, soc=0.5):
        self.kw = batt_kw
        self.size = batt_kwh if (self.kw or 0) > 0 else 0
        self.soc = soc
        self.roundtrip_efficiency = batt_roundtrip_efficiency

    def batt_avail(self, n_steps_per_hour):  # kW
        return min(self.size * self.soc * n_steps_per_hour, self.kw)

    def batt_discharge(self, discharge, n_steps_per_hour):  # kW
        discharge = min(self.batt_avail(n_steps_per_hour), discharge)
        self.soc -= min(discharge / self.size / n_steps_per_hour, self.soc) if self.size > 0 else 0
        return discharge

    def batt_charge(self, charge, n_steps_per_hour):  # kw
        room = (1 - self.soc)  # if there's room in the battery
        charge = min(room * n_steps_per_hour * self.size / self.roundtrip_efficiency, charge,
                     self.kw / self.roundtrip_efficiency)
        chargesoc = charge * self.roundtrip_efficiency / self.size / n_steps_per_hour if self.size > 0 else 0
        self.soc += chargesoc
        return charge

class NoGenerator():
    def __init__(self, diesel_kw, fuel_available, b, m, diesel_min_turndown):
        self.kw = 0
        self.fuel_available = 0
        self.genmin = 0

    def gen_avail(self, n_steps_per_hour):  # kW
        return 0

    def fuel_consume(self, gen_output, n_steps_per_hour):  # kW
        return 0

class NoBattery():
    def __init__(self, batt_kwh, batt_kw, batt_roundtrip_efficiency, soc=0.5):
        self.kw = 0
        self.size = 0

    def batt_avail(self, n_steps_per_hour):  # kW
        return 0

    def batt_discharge(self, discharge, n_steps_per_hour):  # kW
        return 0

    def batt_charge(self, charge, n_steps_per_hour):  # kw
        return 0

def simulate_outage(batt_kwh=0, batt_kw=0, pv_kw_ac_hourly=0, init_soc=0, critical_loads_kw=[], wind_kw_ac_hourly=None,
                    batt_roundtrip_efficiency=0.829, diesel_kw=0, fuel_available=0, b=0, m=0, diesel_min_turndown=0.3,
                    ):
    """
    :param batt_kwh: float, battery storage capacity
    :param batt_kw: float, battery inverter capacity
    :param pv_kw_ac_hourly: list of floats, AC production of PV system
    :param init_soc: list of floats between 0 and 1 inclusive, initial state-of-charge
    :param critical_loads_kw: list of floats
    :param wind_kw_ac_hourly: list of floats, AC production of wind turbine
    :param batt_roundtrip_efficiency: roundtrip battery efficiency
    :param diesel_kw: float, diesel generator capacity
    :param fuel_available: float, gallons of diesel fuel available
    :param b: float, diesel fuel burn rate intercept coefficient (y = m*x + b*rated_capacity)  [gal/kwh/kw]
    :param m: float, diesel fuel burn rate slope (y = m*x + b*rated_capacity)  [gal/kWh]
    :param diesel_min_turndown: minimum generator turndown in fraction of generator capacity (0 to 1)
    :return: list of hours survived for outages starting at every time step, plus min,max,avg of list
    """
<<<<<<< HEAD
    # capping fuel availability to 660 - default fuel availability is set at 1e9 for the optimization process
    # for the outage simulator, the fuel availability is capped at 660.
    if fuel_available == 1e9:
        fuel_available = 660


    if financial_check == "financial_check":
        # Do financial check
        if resilience_run_site_result.keys() == financial_run_site_result.keys():
            for k, v in resilience_run_site_result.items():
                if k in financial_run_site_result:
                    if float(v - financial_run_site_result[k]) / float(max(v, 1)) > 1.0e-3:
                        return False
            return True
        else:
            return False

=======
    n_timesteps = len(critical_loads_kw)
    n_steps_per_hour = n_timesteps / 8760  # type: int

    r = [0] * n_timesteps

    # NOTE: not making hourly load assumptions: a kW is not equivalent to a kWh!!!

    if batt_kw == 0 or batt_kwh == 0:
        init_soc = [0] * n_timesteps  # default is None

        if ((pv_kw_ac_hourly in [None, []]) or (sum(pv_kw_ac_hourly) == 0)) and diesel_kw == 0:  # no pv, generator, nor battery --> no resilience

            months = 12
            hours = 24
            probs_of_surviving_by_month = [[0] for _ in range(months)]
            probs_of_surviving_by_hour_of_the_day = [[0] for _ in range(hours)]
            return {"resilience_by_timestep": r,
                    "resilience_hours_min": 0,
                    "resilience_hours_max": 0,
                    "resilience_hours_avg": 0,
                    "outage_durations": [],
                    "probs_of_surviving": [],
                    "probs_of_surviving_by_month": probs_of_surviving_by_month,
                    "probs_of_surviving_by_hour_of_the_day": probs_of_surviving_by_hour_of_the_day,
                    }

    if pv_kw_ac_hourly in [None, []]:
        pv_kw_ac_hourly = [0] * n_timesteps
    if wind_kw_ac_hourly in [None, []]:
        wind_kw_ac_hourly = [0] * n_timesteps

    def load_following(critical_load, pv, wind, generator, battery, n_steps_per_hour):
        """
        Dispatch strategy for one time step
        """

        # distributed generation minus load is the burden on battery
        unmatch = (critical_load - pv - wind)  # kw

        if unmatch < 0:    # pv + wind> critical_load
            # excess PV power to charge battery
            charge = battery.batt_charge(-unmatch, n_steps_per_hour)
            unmatch = 0

        elif generator.genmin <= generator.gen_avail(n_steps_per_hour) and 0 < generator.kw:
            gen_output = generator.fuel_consume(unmatch, n_steps_per_hour)
            # charge battery with excess energy if unmatch < genmin
            charge = battery.batt_charge(max(gen_output - unmatch, 0), n_steps_per_hour)  # prevent negative charge
            discharge = battery.batt_discharge(max(unmatch - gen_output, 0), n_steps_per_hour)  # prevent negative discharge
            unmatch -= (gen_output + discharge - charge)

        elif unmatch <= battery.batt_avail(n_steps_per_hour):   # battery can carry balance
            discharge = battery.batt_discharge(unmatch, n_steps_per_hour)
            unmatch = 0

        return unmatch, generator, battery

    '''
    Simulation starts here
    '''
    if diesel_kw == 0 or fuel_available == 0:
        GEN = NoGenerator(diesel_kw, fuel_available, b, m, diesel_min_turndown)
>>>>>>> 6cf671b3... clarify what "financial_check" does
    else:
        GEN = Generator(diesel_kw, fuel_available, b, m, diesel_min_turndown)

    if batt_kw == 0 or batt_kwh == 0:
        BATT = NoBattery(batt_kwh, batt_kw, batt_roundtrip_efficiency)
    else:
        BATT = Battery(batt_kwh, batt_kw, batt_roundtrip_efficiency)

    for time_step in range(n_timesteps):
        gen = copy.deepcopy(GEN)
        batt = copy.deepcopy(BATT)
        # outer loop: do simulation starting at each time step
        batt.soc = init_soc[time_step]   # reset battery for each simulation

        for i in range(n_timesteps):    # the i-th time step of simulation
            # inner loop: step through all possible surviving time steps
            # break inner loop if can not survive
            t = (time_step + i) % n_timesteps

            unmatch, gen, batt = load_following(
                critical_loads_kw[t], pv_kw_ac_hourly[t], wind_kw_ac_hourly[t], gen, batt, n_steps_per_hour)

            if unmatch > 0 or i == (n_timesteps-1):  # cannot survive
                r[time_step] = float(i) / float(n_steps_per_hour)
                break

    r_min = min(r)
    r_max = max(r)
    r_avg = round((float(sum(r)) / float(len(r))), 2)

    # Create a time series of 8760*n_steps_per_hour elements starting on 1/1/2017
    time = pd.date_range('1/1/2017', periods=8760*n_steps_per_hour, freq='{}min'.format(n_steps_per_hour*60))
    r_series = pd.Series(r, index=time)

    r_group_month = r_series.groupby(r_series.index.month)
    r_group_hour = r_series.groupby(r_series.index.hour)

    x_vals = list(range(1, int(floor(r_max)+1)))
    y_vals = list()
    y_vals_group_month = list()
    y_vals_group_hour = list()

    for hrs in x_vals:
        y_vals.append(round(float(sum([1 if h >= hrs else 0 for h in r])) / float(n_timesteps), 4))

    width = 0
    for k, v in r_group_month:
        tmp = list()
        max_hr = int(v.max()) + 1
        for hrs in range(max_hr):
            tmp.append(round(float(sum([1 if h >= hrs else 0 for h in v])) / float(len(v)), 4))
        y_vals_group_month.append(tmp)
        if max_hr > width:
            width = max_hr

    # PostgreSQL requires that the arrays are rectangular
    for i, v in enumerate(y_vals_group_month):
        y_vals_group_month[i] = v + [0] * (width - len(v))

    width = 0
    for k, v in r_group_hour:
        tmp = list()
        max_hr = int(v.max()) + 1
        for hrs in range(max_hr):
            tmp.append(round(float(sum([1 if h >= hrs else 0 for h in v])) / float(len(v)), 4))
        y_vals_group_hour.append(tmp)
        if max_hr > width:
            width = max_hr

    # PostgreSQL requires that the arrays are rectangular
    for i, v in enumerate(y_vals_group_hour):
        y_vals_group_hour[i] = v + [0] * (width - len(v))

    return {"resilience_by_timestep": r,
            "resilience_hours_min": r_min,
            "resilience_hours_max": r_max,
            "resilience_hours_avg": r_avg,
            "outage_durations": x_vals,
            "probs_of_surviving": y_vals,
            "probs_of_surviving_by_month": y_vals_group_month,
            "probs_of_surviving_by_hour_of_the_day": y_vals_group_hour,
            }
