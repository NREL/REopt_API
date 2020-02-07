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

def simulate_outage(batt_kwh, batt_kw, pv_kw_ac_hourly, init_soc, critical_loads_kw, wind_kw_ac_hourly=None,
                    batt_roundtrip_efficiency=0.829, diesel_kw=0, fuel_available=0, b=0, m=0, diesel_min_turndown=0.3, financial_outage_sim=None):
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
    :param b: float, diesel fuel burn rate intercept (y=mx+b)  [gal/timestep]
    :param m: float, diesel fuel burn rate slope     (y=mx+b)  [gal/kW-timestep]
    :param diesel_min_turndown: minimum generator turndown in fraction of generator capacity (0 to 1)
    :return: list of hours survived for outages starting at every time step, plus min,max,avg of list
    """
    n_timesteps = len(critical_loads_kw)
    n_steps_per_hour = n_timesteps / 8760
    r = [0] * n_timesteps  # initialize resiliency vector

    if batt_kw == 0 or batt_kwh == 0:
        init_soc = [0] * n_timesteps  # default is None

        if pv_kw_ac_hourly in [None, []] and diesel_kw == 0:  # no pv, generator, nor battery --> no resilience

            return {"resilience_by_timestep": r,
                    "resilience_hours_min": 0,
                    "resilience_hours_max": 0,
                    "resilience_hours_avg": 0,
                    "outage_durations": None,
                    "probs_of_surviving": None,
                    }

    if pv_kw_ac_hourly in [None, []]:
        pv_kw_ac_hourly = [0] * n_timesteps
    if wind_kw_ac_hourly in [None, []]:
        wind_kw_ac_hourly = [0] * n_timesteps

    # distributed generation minus load is the burden on battery
    # negative values are unmet load
    dGenMld = [pv + wd - ld for (pv, wd, ld) in zip(pv_kw_ac_hourly, wind_kw_ac_hourly, critical_loads_kw)]

    for n in range(n_timesteps):  # outer loop for finding r for outage starting each timestep of year

        charge = batt_kwh * init_soc[n]  # reset battery for each simulation
        fuel_tank_gal = fuel_available   # reset diesel fuel tank

        for bal in dGenMld:  # bal == balance after PV serves load

            if bal >= 0:  # load met by PV
                r[n] += 1  # survived one more timestep

                if charge < batt_kwh:  # if there's room in the battery
                    charge += min(batt_kwh - charge, bal * batt_roundtrip_efficiency, batt_kw)

            else:  # balance < 0 --> load not met by PV
                abs_bal = abs(bal)
                
                if min(charge, batt_kw) >= abs_bal:  # battery can carry balance
                    charge = max(0, charge - abs_bal)  # prevent battery charge from going negative
                    r[n] += 1  # survived one more timestep

                else:  # battery can meet part or no load
                    after_batt_bal = abs_bal - min(charge, batt_kw)
                    charge -= min(charge, batt_kw)  # battery is either drained or maxing out inverter

                    # NOTE: making hourly load assumptions: a kW is equivalent to a kWh!!!
                    generator_output = max(after_batt_bal, diesel_min_turndown * diesel_kw)
                    fuel_needed = m * generator_output + b

                    if after_batt_bal <= diesel_kw and fuel_needed <= fuel_tank_gal:
                        # diesel can meet balance
                        fuel_tank_gal -= fuel_needed
                        r[n] += 1  # survived one more timestep
                    
                    else:  # load not met
                        dGenMld = dGenMld[1:] + dGenMld[:1]  # shift dGenMld one timestep
                        break

    dGenMld = dGenMld[1:] + dGenMld[:1]  # shift back to original state

    r_min = min(r)/n_steps_per_hour
    r_max = max(r)/n_steps_per_hour
    r_avg = round((float(sum(r)) / float(len(r))/n_steps_per_hour), 2)

    x_vals = range(1, int(floor(r_max)+1))
    y_vals = list()
    for hrs in x_vals:
        y_vals.append(round(float(sum([1 if h >= hrs else 0 for h in r])) / float(n_timesteps), 4))
    
    return {"resilience_by_timestep": r,
            "resilience_hours_min": r_min,
            "resilience_hours_max": r_max,
            "resilience_hours_avg": r_avg,
            "outage_durations": x_vals,
            "probs_of_surviving": y_vals,
            }
