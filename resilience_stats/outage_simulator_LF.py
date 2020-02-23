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
from math import floor
import pandas as pd
from celery import group, shared_task
from time import sleep


class Generator(object):
    def __init__(self, diesel_kw, fuel_available, b, m, min_turndown):
        self.kw = diesel_kw
        self.fuel_available = fuel_available if (self.kw or 0) > 0 else 0
        self.b = b  # fuel burn rate intercept (y=mx+b)  [gal/hour]
        self.m = m  # fuel burn rate slope     (y=mx+b)  [gal/kWh]
        self.genmin = min_turndown * self.kw

    def gen_avail(self, n_steps_per_hour):  # kW
        gen_avail = 0
        if self.fuel_available - self.b > 0:
            gen_avail = min((self.fuel_available * n_steps_per_hour - self.b) / self.m, self.kw)
        return gen_avail

    def fuel_consume(self, load, n_steps_per_hour):  # kW
        gen_output = 0
        if self.gen_avail(n_steps_per_hour) >= self.genmin and load > 0:
            gen_output = max(self.genmin, min(load, self.gen_avail(n_steps_per_hour)))
            fuel_consume = (self.b + self.m * gen_output) / n_steps_per_hour
            self.fuel_available -= min(self.fuel_available, fuel_consume)
        return gen_output


class Battery(object):
    def __init__(self, batt_kwh, batt_kw, batt_roundtrip_efficiency, soc=0.5):
        self.kw = batt_kw
        self.kwh = batt_kwh if (self.kw or 0) > 0 else 0
        self.soc = soc
        self.roundtrip_efficiency = batt_roundtrip_efficiency

    def batt_avail(self, n_steps_per_hour):  # kW
        # return min of power to completely drain battery and inverter capacity
        return min(self.kwh * self.soc * n_steps_per_hour, self.kw)

    def batt_discharge(self, discharge, n_steps_per_hour):  # kW
        discharge = min(self.batt_avail(n_steps_per_hour), discharge)
        self.soc -= min(discharge / self.kwh / n_steps_per_hour, self.soc) if self.kwh > 0 else 0
        return discharge

    def batt_charge(self, charge, n_steps_per_hour):  # kw
        room = (1 - self.soc)  # if there's room in the battery
        charge = min(room * n_steps_per_hour * self.kwh / self.roundtrip_efficiency, charge,
                     self.kw)
        chargesoc = charge * self.roundtrip_efficiency / self.kwh / n_steps_per_hour if self.kwh > 0 else 0
        self.soc += chargesoc
        return charge


def load_following(load, generator, battery, n_steps_per_hour):
    """
    Dispatch strategy for one time step
    1. PV and/or Wind
    2. Generator
    3. Battery
    """
    if load < 0:    # pv + wind > critical_load
        # excess PV+Wind charges the battery
        charge = battery.batt_charge(-load, n_steps_per_hour)
        load = 0

    elif generator.genmin <= generator.gen_avail(n_steps_per_hour) and generator.kw > 0:
        gen_output = generator.fuel_consume(load, n_steps_per_hour)
        # charge battery with excess energy if load < genmin
        charge = battery.batt_charge(max(gen_output - load, 0), n_steps_per_hour)  # prevent negative charge
        # discharge battery if load > gen_output
        discharge = battery.batt_discharge(max(load - gen_output, 0), n_steps_per_hour)  # prevent negative discharge
        load -= (gen_output + discharge - charge)

    elif load <= battery.batt_avail(n_steps_per_hour):   # battery can carry balance
        discharge = battery.batt_discharge(load, n_steps_per_hour)
        load = 0

    return load, generator, battery


@shared_task
def simulate_outage(init_time_step, diesel_kw, fuel_available, b, m, diesel_min_turndown, batt_kwh, batt_kw,
                    batt_roundtrip_efficiency, n_timesteps, n_steps_per_hour, batt_soc_kwh, crit_load):
    """
    Determine how long the critical load can be met with gas generator and energy storage
    :param init_time_step:
    :param diesel_kw:
    :param fuel_available: float, gallons
    :param b: float, diesel fuel burn rate intercept coefficient (y = m*x + b)  [gal/hr]
    :param m: float, diesel fuel burn rate slope (y = m*x + b)  [gal/kWh]
    :param diesel_min_turndown:
    :param batt_kwh:
    :param batt_kw:
    :param batt_roundtrip_efficiency:
    :param batt_soc_kwh:
    :param n_timesteps:
    :param n_steps_per_hour:
    :param crit_load:
    :return: float, number of hours that the critical load can be met using load following
    """

    gen = Generator(diesel_kw, fuel_available, b, m, diesel_min_turndown)
    batt = Battery(batt_kwh, batt_kw, batt_roundtrip_efficiency, soc=batt_soc_kwh/batt_kwh)

    for i in range(n_timesteps):
        t = (init_time_step + i) % n_timesteps  # for wrapping around end of year

        unmet_load, gen, batt = load_following(crit_load[t], gen, batt, n_steps_per_hour)

        if round(unmet_load, 5) > 0:  # failed to meet load in this time step
            return float(i) / float(n_steps_per_hour)

    return n_timesteps / n_steps_per_hour  # met the critical load for all time steps


def simulate_outages(batt_kwh=0, batt_kw=0, pv_kw_ac_hourly=0, init_soc=0, critical_loads_kw=[], wind_kw_ac_hourly=None,
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
    :return: dict,
        {
            "resilience_by_timestep": r,
            "resilience_hours_min": r_min,
            "resilience_hours_max": r_max,
            "resilience_hours_avg": r_avg,
            "outage_durations": x_vals,
            "probs_of_surviving": y_vals,
            "probs_of_surviving_by_month": y_vals_group_month,
            "probs_of_surviving_by_hour_of_the_day": y_vals_group_hour,
        }
    """
    n_timesteps = len(critical_loads_kw)
    n_steps_per_hour = int(n_timesteps / 8760)
    r = [0] * n_timesteps

    if batt_kw == 0 or batt_kwh == 0:
        init_soc = [0] * n_timesteps  # default is None

        if ((pv_kw_ac_hourly in [None, []]) or (sum(pv_kw_ac_hourly) == 0)) and diesel_kw == 0:
            # no pv, generator, nor battery --> no resilience
            return {"resilience_by_timestep": r,
                    "resilience_hours_min": 0,
                    "resilience_hours_max": 0,
                    "resilience_hours_avg": 0,
                    "outage_durations": [],
                    "probs_of_surviving": [],
                    "probs_of_surviving_by_month": [[0] for _ in range(12)],
                    "probs_of_surviving_by_hour_of_the_day": [[0] for _ in range(24)],
                    }

    if pv_kw_ac_hourly in [None, []]:
        pv_kw_ac_hourly = [0] * n_timesteps
    if wind_kw_ac_hourly in [None, []]:
        wind_kw_ac_hourly = [0] * n_timesteps
    '''
    Simulation starts here
    '''
    load_minus_der = [ld - pv - wd for (pv, wd, ld) in zip(pv_kw_ac_hourly, wind_kw_ac_hourly, critical_loads_kw)]
    
    # outer loop: do simulation starting at each time step
    jobs = group(simulate_outage.s(
        init_time_step=time_step,
        diesel_kw=diesel_kw,
        fuel_available=fuel_available,
        b=b, m=m,
        diesel_min_turndown=diesel_min_turndown,
        batt_kwh=batt_kwh,
        batt_kw=batt_kw,
        batt_roundtrip_efficiency=batt_roundtrip_efficiency,
        n_timesteps=n_timesteps,
        n_steps_per_hour=n_steps_per_hour,
        batt_soc_kwh=init_soc[time_step]*batt_kwh,
        crit_load=load_minus_der) for time_step in range(n_timesteps)
    )
    result = jobs()
    while not result.ready():
        sleep(2)
    if result.failed():
        raise Exception("Outage simulator failed.")
    r = result.get()

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
