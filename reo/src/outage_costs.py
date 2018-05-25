from resilience_stats.outage_simulator import simulate_outage


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
    """
    site_inputs = data['inputs']['Scenario']['Site']
    site_outputs = data['outputs']['Scenario']['Site']
    load = site_outputs['LoadProfile'].get('year_one_electric_load_series_kw', 8760*[0])
    batt_roundtrip_efficiency = site_inputs['Storage']['internal_efficiency_pct'] \
                                * site_inputs['Storage']['inverter_efficiency_pct'] \
                                * site_inputs['Storage']['rectifier_efficiency_pct']
    critical_loads_kw=site_inputs['LoadProfile'].get("critical_loads_kw")
    critical_loads_kw_is_net=site_inputs['LoadProfile'].get("critical_loads_kw_is_net")
    crit_load_factor = site_inputs['LoadProfile'].get("critical_load_pct")

    results = simulate_outage(
        pv_kw=site_inputs['PV'].get('existing_kw', 0) + site_outputs['PV'].get('size_kw', 0),
        batt_kwh=site_outputs['Storage'].get('size_kwh', 0),
        batt_kw=site_outputs['Storage'].get('size_kw', 0),
        load=load,
        pv_kw_ac_hourly=site_outputs['PV'].get('year_one_power_production_series_kw'),
        init_soc=site_outputs['Storage'].get('year_one_soc_series_pct'),
        critical_loads_kw=critical_loads_kw,
        critical_loads_kw_is_net=critical_loads_kw_is_net,
        crit_load_factor=crit_load_factor,
        batt_roundtrip_efficiency=batt_roundtrip_efficiency,
        diesel_kw=site_inputs['Generator']['size_kw'],
        fuel_available=site_inputs['Generator']['fuel_avail_gal'],
        b=site_inputs['Generator']['fuel_intercept_gal_per_hr'],
        m=site_inputs['Generator']['fuel_slope_gal_per_kwh'],
        diesel_min_turndown=site_inputs['Generator']['min_turn_down_pct']
    )

    avg_crit_ld = sum(load) * crit_load_factor / len(load)

    if site_inputs['LoadProfile'].get('outage_is_major_event') is True:
        # assume that outage occurs only once in analysis period
        present_worth_factor = 1

    data['outputs']['Scenario']['Site']['Financial']['avoided_outage_costs_us_dollars'] = round(
        site_inputs['Financial']['value_of_lost_load_us_dollars_per_kwh']
        * results['resilience_hours_avg']
        * avg_crit_ld
        * present_worth_factor, 2)
