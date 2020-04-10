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
from resilience_stats.outage_simulator_LF import simulate_outage
import numpy as np

def calc_avoided_outage_costs(data, present_worth_factor):
    """
    Add output parameter to data:
        data['outputs']['Scenario']['Site']['avoided_outage_costs_us_dollars']
            = VoLL X avg_hrs_sustained X avg_crit_ld X present_worth_factor
    :param data: nested dict used for API response
    :param present_worth_factor: float, accounts for escalation and discount of avoided outage costs over analysis
        period. NOTE: we use pwf_e from REopt, which uses the electricity cost escalation rate and offtaker
        discount rate.
    :return: None

    NOTE: we cannot use resilience_stats endpoint for this calculation because it relies on the results already being
    saved to the DB, and calculating the outage costs is done before the results are saved because it is one of the
    results.
    """
    site_inputs = data['inputs']['Scenario']['Site']
    site_outputs = data['outputs']['Scenario']['Site']
    pvs = site_outputs['PV']
    wind = site_outputs['Wind']
    generator = site_outputs['Generator']
    load_profile = site_inputs['LoadProfile']
    batt_roundtrip_efficiency = site_inputs['Storage']['internal_efficiency_pct'] \
                                * site_inputs['Storage']['inverter_efficiency_pct'] \
                                * site_inputs['Storage']['rectifier_efficiency_pct']
    critical_load = site_outputs['LoadProfile']['critical_load_series_kw']
    
    pv_production = []
    for p in pvs:
        add_prod = p.get('year_one_power_production_series_kw') or []
        if add_prod != []:
            if pv_production == []:
                pv_production = add_prod
            else:
                pv_production += np.array(add_prod)
    if sum(pv_production) == 0:
        pv_production = []

    results = simulate_outage(
        batt_kwh=site_outputs['Storage'].get('size_kwh') or 0,
        batt_kw=site_outputs['Storage'].get('size_kw') or 0,
        pv_kw_ac_hourly=list(pv_production),
        wind_kw_ac_hourly=wind['year_one_power_production_series_kw'],
        init_soc=site_outputs['Storage'].get('year_one_soc_series_pct'),
        critical_loads_kw=critical_load,
        batt_roundtrip_efficiency=batt_roundtrip_efficiency,
        diesel_kw=generator['size_kw'],
        fuel_available=site_inputs['Generator']['fuel_avail_gal'],
        b=site_inputs['Generator']['fuel_intercept_gal_per_hr'],
        m=site_inputs['Generator']['fuel_slope_gal_per_kwh'],
        diesel_min_turndown=site_inputs['Generator']['min_turn_down_pct']
    )

    avg_crit_ld = sum(critical_load) / len(critical_load)

    if load_profile['outage_is_major_event']:
        # assume that outage occurs only once in analysis period
        present_worth_factor = 1

    data['outputs']['Scenario']['Site']['Financial']['avoided_outage_costs_us_dollars'] = round(
        site_inputs['Financial']['value_of_lost_load_us_dollars_per_kwh']
        * results['resilience_hours_avg']
        * avg_crit_ld
        * present_worth_factor, 2)
