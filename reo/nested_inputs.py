max_big_number = 1e8
max_incentive = 1e10
max_years = 75
macrs_schedules = [0, 5, 7]
analysis_years = 20
providers = ['federal', 'state', 'utility']
default_buildings = ['FastFoodRest',
                     'FullServiceRest',
                     'Hospital',
                     'LargeHotel',
                     'LargeOffice',
                     'MediumOffice',
                     'MidriseApartment',
                     'Outpatient',
                     'PrimarySchool',
                     'RetailStore',
                     'SecondarySchool',
                     'SmallHotel',
                     'SmallOffice',
                     'StripMall',
                     'Supermarket',
                     'Warehouse',
                     ]


def list_of_float(input):
    return [float(i) for i in input]

nested_input_definitions = {

    "Scenario": {
                "timeout_seconds":      {'type': float,'min': 1, 'max': 295, 'default': 295},
                "user_id":              {'type': str},
                "time_steps_per_hour":  {'type': float, 'min': 1, 'max': 1, 'default': 1}, # aspirational - we only handle 1 timestep per hour

        "Site": {
                     "latitude":            {'type': float, 'min':-180, 'max':180, 'required': True},
                     "longitude":           {'type': float, 'min':-180, 'max':180, 'required': True},
                     "land_acres":          {'type': float, 'min': 0, 'max': 1e6},
                     "roof_squarefeet":     {'type': float, 'min': 0, 'max': 1e9},

            "Financial": {
                    "om_cost_growth_pct":   {'type': float, 'min': -1, 'max': 1, 'default': 0.025},
                    "escalation_pct":       {'type': float,'min': -1, 'max': 1, 'default': 0.026},
                    "owner_tax_pct":        {'type': float,'min': -1, 'max': 1},
                    "offtaker_tax_pct":     {'type': float,'min': -1, 'max': 1, 'default': 0.4},
                    "owner_discount_pct":   {'type': float,'min': -1, 'max': 1},
                    "offtaker_discount_pct":{'type': float,'min': -1, 'max': 1, 'default': 0.081},
                    "analysis_years":       {'type': int,'min': 0, 'max': max_years, 'default': analysis_years}
         },

            "LoadProfile": {
                            "doe_reference_name":   {'type': str, 'restrict_to':default_buildings},
                            "annual_kwh":           {'type': float, 'min': 0, 'max': 1e12},
                            "year":                 {'type': int, 'min': 2017, 'max': 2017+max_years, 'default': 2018},
                            "monthly_totals_kwh":   {'type': list_of_float},
                            "loads_kw":             {'type': list_of_float},
                            "outage_start_hour":    {'type': int, 'min': 0, 'max': 8759},
                            "outage_end_hour":      {'type': int , 'min': 0, 'max': 8759},
                            "critical_load_pct":    {'type': float, 'min': 0, 'max': 1, 'default': 0.5},
                     },

            "ElectricTariff": {
                                "urdb_utilty_name":                         {'type': str},
                                "urdb_rate_name":                           {'type': str},
                                "blended_monthly_rates_us_dollars_per_kwh": {'type': list_of_float},
                                "monthly_demand_charges_us_dollars_per_kw": {'type': list_of_float},
                                "net_metering_limit_kw":                    {'type': float,'min': 0, 'max': 1e9, 'default':0},
                                "interconnection_limit_kw":                 {'type': float,'min': 0, 'max': 1e9,'default': max_big_number},
                                "wholesale_rate_us_dollars_per_kwh":        {'type': float, 'min': 0, 'default': 0},
                                "urdb_response":                            {'type': dict},
                                "urdb_label":                               {'type': str}
                           },

            "Wind": {
                                "min_kw":                               {'type': float, 'min': 0, 'max': 1e9, 'default': 0},
                                "max_kw":                               {'type': float, 'min': 0, 'max': 1e9, 'default': 0},
                                "installed_cost_us_dollars_per_kw":     {'type': float, 'min': 0, 'max': 1e5, 'default': 2000},
                                "om_cost_us_dollars_per_kw":            {'type': float, 'min': 0, 'max': 1e3, 'default': 35},
                                "macrs_option_years":                   {'type': int, 'restrict_to': macrs_schedules, 'default': 5},
                                "macrs_bonus_pct":                      {'type': float, 'min': 0, 'max': 1, 'default': 0.5},
                                "macrs_itc_reduction":                  {'type': float, 'min': 0, 'max': 1, 'default': 0.5},
                                "federal_itc_pct":                      {'type': float,'min': 0, 'max': 1, 'default': 0.3},
                                "state_ibi_pct":                        {'type': float,'min': 0, 'max': 1, 'default': 0},
                                "state_ibi_max_us_dollars":             {'type': float,'min': 0, 'max': 1e10, 'default': max_incentive},
                                "utility_ibi_pct":                      {'type': float,'min': 0, 'max': 1, 'default': 0},
                                "utility_ibi_max_us_dollars":           {'type': float,'min': 0, 'max': 1e10, 'default': max_incentive},
                                "federal_rebate_us_dollars_per_kw":     {'type': float,'min': 0, 'max': 1e9, 'default': 0},
                                "state_rebate_us_dollars_per_kw":       {'type': float,'min': 0, 'max': 1e9, 'default': 0},
                                "state_rebate_max_us_dollars":          {'type': float,'min': 0, 'max': 1e10, 'default': max_incentive},
                                "utility_rebate_us_dollars_per_kw":     {'type': float,'min': 0, 'max': 1e9, 'default': 0},
                                "utility_rebate_max_us_dollars":        {'type': float,'min': 0, 'max': 1e10, 'default': max_incentive},
                                "pbi_us_dollars_per_kwh":               {'type': float,'min': 0, 'max': 1e9, 'default': 0},
                                "pbi_max_us_dollars":                   {'type': float,'min': 0, 'max': 1e9, 'default': 1e9},
                                "pbi_years":                            {'type': float,'min': 0, 'max': 1e9, 'default': analysis_years},
                                "pbi_system_max_kw":                    {'type': float,'min': 0, 'max': 1e9, 'default': 1e9},
                             },

            "PV": {
                                "min_kw":                               {'type': float, 'min': 0, 'max': 1e9, 'default': 0},
                                "max_kw":                               {'type': float, 'min': 0, 'max': 1e9, 'default': 1e9},
                                "installed_cost_us_dollars_per_kw":     {'type': float, 'min': 0, 'max': 1e5, 'default': 2000},
                                "om_cost_us_dollars_per_kw":            {'type': float, 'min': 0, 'max': 1e3, 'default': 16},
                                "degradation_pct":                      {'type': float, 'min': 0, 'max': 1, 'default': 0.005},
                                "macrs_option_years":                   {'type': int, 'restrict_to': macrs_schedules, 'default': 5},
                                "macrs_bonus_pct":                      {'type': float, 'min': 0, 'max': 1, 'default': 0.5},
                                "macrs_itc_reduction":                  {'type': float, 'min': 0, 'max': 1, 'default': 0.5},
                                "federal_itc_pct":                      {'type': float,'min': 0, 'max': 1, 'default': 0.3},
                                "state_ibi_pct":                        {'type': float,'min': 0, 'max': 1, 'default': 0},
                                "state_ibi_max_us_dollars":             {'type': float,'min': 0, 'max': 1e10, 'default': max_incentive},
                                "utility_ibi_pct":                      {'type': float,'min': 0, 'max': 1, 'default': 0},
                                "utility_ibi_max_us_dollars":           {'type': float,'min': 0, 'max': 1e10, 'default':max_incentive},
                                "federal_rebate_us_dollars_per_kw":     {'type': float,'min': 0, 'max': 1e9, 'default': 0},
                                "state_rebate_us_dollars_per_kw":       {'type': float,'min': 0, 'max': 1e9, 'default': 0},
                                "state_rebate_max_us_dollars":          {'type': float,'min': 0, 'max': 1e10, 'default': max_incentive},
                                "utility_rebate_us_dollars_per_kw":     {'type': float,'min': 0, 'max': 1e9, 'default': 0},
                                "utility_rebate_max_us_dollars":        {'type': float,'min': 0, 'max': 1e10, 'default': max_incentive},
                                "pbi_us_dollars_per_kwh":               {'type': float,'min': 0, 'max': 1e9, 'default': 0},
                                "pbi_max_us_dollars":                   {'type': float,'min': 0, 'max': 1e9, 'default': 1e9},
                                "pbi_years":                            {'type': float,'min': 0 , 'max': 1e9, 'default': analysis_years},
                                "pbi_system_max_kw":                    {'type': float,'min': 0, 'max': 1e9, 'default': 1e9},
                                "azimuth":                              {'type': float, 'min': 0, 'max': 360, 'default': 180},
                                "losses":                               {'type': float,'min': 0, 'max': 0.99, 'default': 0.14},
                                "array_type":                           {'type': int, 'restrict_to': [0, 1, 2, 3, 4], 'default': 0},
                                "module_type":                          {'type': int, 'restrict_to': [0, 1, 2], 'default': 0},
                                "gcr":                                  {'type': float, 'min': 0.01, 'max': 0.99, 'default': 0.4},
                                "dc_ac_ratio":                          {'type': float, 'min': 0, 'max': 2, 'default': 1.1},
                                "inv_eff":                              {'type': float ,'min': 0.9, 'max': 0.995, 'default': 0.96},
                                "radius":                               {'type': float , 'min': 0, 'default': 0},
                                "tilt":                                 {'type': float, 'min': 0, 'max': 90}
                             },

            "Storage": {
                            "min_kw":                               {'type': float,'min': 0, 'max': 1e9, 'default': 0},
                            "max_kw":                               {'type': float,'min': 0, 'max': 1e9, 'default': 1000000},
                            "min_kwh":                              {'type': float,'min': 0, 'default': 0},
                            "max_kwh":                              {'type': float,'min': 0, 'default': 1000000},
                            "internal_efficiency_pct":              {'type': float, 'min': 0, 'max': 1, 'default': 0.975},
                            "inverter_efficiency_pct":              {'type': float, 'min': 0, 'max': 1, 'default': 0.96},
                            "rectifier_efficiency_pct":             {'type': float, 'min': 0, 'max': 1, 'default': 0.96},
                            "soc_min_pct":                          {'type': float, 'min': 0, 'max': 1, 'default': 0.2},
                            "soc_init_pct":                         {'type': float, 'min': 0, 'max': 1, 'default': 0.5},
                            "canGridCharge":                        {'type': bool, 'default': False},
                            "installed_cost_us_dollars_per_kw":     {'type': float,'min': 0, 'max': 1e4, 'default': 1000},
                            "installed_cost_us_dollars_per_kwh":    {'type': float,'min': 0, 'max': 1e4, 'default': 500},
                            "replace_cost_us_dollars_per_kw":       {'type': float, 'min': 0, 'max': 1e4, 'default': 460},
                            "replace_cost_us_dollars_per_kwh":      {'type': float,'min': 0, 'max': 1e4, 'default': 230},
                            "inverter_replacement_year":            {'type': float, 'min': 0, 'max': max_years, 'default': 10},
                            "battery_replacement_year":             {'type': float, 'min': 0, 'max': max_years, 'default': 10},
                            "macrs_option_years":                   {'type': int, 'restrict_to': macrs_schedules, 'default': 5},
                            "macrs_bonus_pct":                      {'type': float, 'min': 0, 'max': 1, 'default': 0.5},
                            "macrs_itc_reduction":                  {'type': float, 'min': 0, 'max': 1, 'default': 0.5},
                            "total_itc_pct":                        {'type': float,'min': 0, 'max': 1, 'default': 0.3},
                            "total_rebate_us_dollars_per_kw":       {'type': float,'min': 0, 'max': 1e9, 'default': 0},
     },
     },
 },
}


def flat_to_nested(i):

    return {
        "Scenario": {
            "timeout_seconds": i.get("timeout"),
            "user_id": i.get("user_id"),
            "time_steps_per_hour": i.get("time_steps_per_hour"),

            "Site": {
                "latitude": i.get("latitude"),
                "longitude": i.get("longitude"),
                "land_acres": i.get("land_area"),
                "roof_squarefeet": i.get("roof_area"),

                "Financial": {
                                "om_cost_growth_pct": i.get("om_cost_growth_rate"),
                                "escalation_pct": i.get("rate_escalation"),
                                "owner_tax_pct": i.get("owner_tax_rate"),
                                "offtaker_tax_pct": i.get("offtaker_tax_rate"),
                                "owner_discount_pct": i.get("owner_discount_rate"),
                                "offtaker_discount_pct": i.get("offtaker_discount_rate"),
                                "analysis_years": i.get("analysis_period"),
             },

                "LoadProfile":
                    {
                        "doe_reference_name": i.get("load_profile_name"),
                        "annual_kwh": i.get("load_size"),
                        "year": i.get("load_year"),
                        "monthly_totals_kwh": i.get("load_monthly_kwh"),
                        "loads_kw": i.get("load_8760_kw"),
                        "outage_start_hour": i.get("outage_start"),
                        "outage_end_hour": i.get("outage_end"),
                        "critical_load_pct": i.get("crit_load_factor"),
                 },

                "ElectricTariff":
                    {
                        "urdb_utilty_name": i.get("utility_name"),
                        "urdb_rate_name": i.get("rate_name"),
                        "urdb_response": i.get("urdb_rate"),
                        "blended_monthly_rates_us_dollars_per_kwh": i.get("blended_utility_rate"),
                        "monthly_demand_charges_us_dollars_per_kw": i.get("demand_charge"),
                        "net_metering_limit_kw": i.get("net_metering_limit"),
                        "wholesale_rate_us_dollars_per_kwh": i.get("wholesale_rate"),
                        "interconnection_limit_kw": i.get("interconnection_limit"),
                 },

                "PV":
                    {
                        "min_kw": i.get("pv_kw_min"),
                        "max_kw": i.get("pv_kw_max"),
                        "installed_cost_us_dollars_per_kw": i.get("pv_cost"),
                        "om_cost_us_dollars_per_kw": i.get("pv_om"),
                        "degradation_pct": i.get("pv_degradation_rate"),
                        "azimuth": i.get("azimuth"),
                        "losses": i.get("losses"),
                        "array_type": i.get("array_type"),
                        "module_type": i.get("module_type"),
                        "gcr": i.get("gcr"),
                        "dc_ac_ratio": i.get("dc_ac_ratio"),
                        "inv_eff": i.get("inv_eff"),
                        "radius": i.get("radius"),
                        "tilt": i.get("tilt"),
                        "macrs_option_years": i.get("pv_macrs_schedule"),
                        "macrs_bonus_pct": i.get("pv_macrs_bonus_fraction"),
                        "macrs_itc_reduction": i.get("pv_macrs_itc_reduction"),
                        "federal_itc_pct": i.get("pv_itc_federal"),
                        "state_ibi_pct": i.get("pv_itc_state"),
                        "state_ibi_max_us_dollars": i.get("pv_ibi_state_max"),
                        "utility_ibi_pct": i.get("pv_ibi_utility"),
                        "utility_ibi_max_us_dollars": i.get("pv_ibi_utility_max"),
                        "federal_rebate_us_dollars_per_kw": i.get("pv_rebate_federal"),
                        "state_rebate_us_dollars_per_kw": i.get("pv_rebate_state"),
                        "state_rebate_max_us_dollars": i.get("pv_rebate_state_max"),
                        "utility_rebate_us_dollars_per_kw": i.get("pv_rebate_utility"),
                        "utility_rebate_max_us_dollars":i.get("pv_rebate_utility_max"),
                        "pbi_us_dollars_per_kwh": i.get("pv_pbi"),
                        "pbi_max_us_dollars": i.get("pv_pbi_max"),
                        "pbi_years": i.get("pv_pbi_years"),
                        "pbi_system_max_kw": i.get("pv_pbi_system_max"),
                 },

                "Wind":
                    {
                        "min_kw": i.get("wind_kw_min"),
                        "max_kw": i.get("wind_kw_max"),
                        "installed_cost_us_dollars_per_kw": i.get("wind_cost"),
                        "om_cost_us_dollars_per_kw": i.get("wind_om"),
                        "degradation_pct": i.get("wind_degradation_rate"),
                        "macrs_option_years": i.get("wind_macrs_schedule"),
                        "macrs_bonus_pct": i.get("wind_macrs_bonus_fraction"),
                        "macrs_itc_reduction": i.get("wind_macrs_itc_reduction"),
                        "federal_itc_pct": i.get("wind_itc_federal"),
                        "state_ibi_pct": i.get("wind_ibi_state"),
                        "state_ibi_max_us_dollars": i.get("wind_ibi_state_max"),
                        "utility_ibi_pct": i.get("wind_ibi_utility"),
                        "utility_ibi_max_us_dollars": i.get("wind_ibi_utility_max"),
                        "federal_rebate_us_dollars_per_kw": i.get("wind_rebate_federal"),
                        "state_rebate_us_dollars_per_kw": i.get("wind_rebate_state"),
                        "state_rebate_max_us_dollars": i.get("wind_rebate_state_max"),
                        "utility_rebate_us_dollars_per_kw": i.get("wind_rebate_utility"),
                        "utility_rebate_max_us_dollars": i.get("wind_rebate_utility_max"),
                        "pbi_us_dollars_per_kwh": i.get("wind_pbi"),
                        "pbi_max_us_dollars": i.get("wind_pbi_max"),
                        "pbi_years": i.get("wind_pbi_years"),
                        "pbi_system_max_kw": i.get("wind_pbi_system_max"),
                 },

                "Storage":
                    {
                    "min_kw": i.get("batt_kw_min"),
                    "max_kw": i.get("batt_kw_max"),
                    "min_kwh": i.get("batt_kwh_min"),
                    "max_kwh": i.get("batt_kwh_max"),
                    "internal_efficiency_pct": i.get("batt_efficiency"),
                    "inverter_efficiency_pct": i.get("batt_inverter_efficiency"),
                    "rectifier_efficiency_pct": i.get("batt_rectifier_efficiency"),
                    "soc_min_pct": i.get("batt_soc_min"),
                    "soc_init_pct": i.get("batt_soc_init"),
                    "canGridCharge": i.get("batt_can_gridcharge"),
                    "installed_cost_us_dollars_per_kw": i.get("batt_cost_kw"),
                    "installed_cost_us_dollars_per_kwh": i.get("batt_cost_kwh"),
                    "replace_cost_us_dollars_per_kw": i.get("batt_replacement_cost_kw"),
                    "replace_cost_us_dollars_per_kwh": i.get("batt_replacement_cost_kwh"),
                    "inverter_replacement_year": i.get("batt_replacement_year_kw"),
                    "battery_replacement_year": i.get("batt_replacement_year_kwh"),
                    "macrs_option_years": i.get("batt_macrs_schedule"),
                    "macrs_bonus_pct": i.get("batt_macrs_bonus_fraction"),
                    "macrs_itc_reduction": i.get("batt_macrs_itc_reduction"),
                    "total_itc_pct":  i.get("batt_itc_total"),
                    "total_rebate_us_dollars_per_kw": i.get("batt_rebate_total"),
             },
         },
     },
 }
