from resilience_stats.outage_simulator_LF import simulate_outage


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
    pv = site_outputs['PV']
    wind = site_outputs['Wind']
    generator = site_outputs['Generator']
    load_profile = site_inputs['LoadProfile']
    batt_roundtrip_efficiency = site_inputs['Storage']['internal_efficiency_pct'] \
                                * site_inputs['Storage']['inverter_efficiency_pct'] \
                                * site_inputs['Storage']['rectifier_efficiency_pct']
    critical_load = site_outputs['LoadProfile']['critical_load_series_kw']

    results = simulate_outage(
        batt_kwh=site_outputs['Storage'].get('size_kwh', 0),
        batt_kw=site_outputs['Storage'].get('size_kw', 0),
        pv_kw_ac_hourly=pv['year_one_power_production_series_kw'],
        wind_kw_ac_hourly=wind['year_one_power_production_series_kw'],
        init_soc=site_outputs['Storage'].get('year_one_soc_series_pct'),
        critical_loads_kw=critical_load,
        batt_roundtrip_efficiency=batt_roundtrip_efficiency,
        diesel_kw=generator['size_kw'],
        # in-case of unlimited fuel the outage simulator slows downs because of 8760 X 8760 iterations
        # therefore limiting the fuel availability to 660 gallons
        #fuel_available=site_inputs['Generator']['fuel_avail_gal'],
        fuel_available=660,
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
