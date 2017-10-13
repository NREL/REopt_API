max_big_number = 1e8
max_incentive = 1e10
max_years = 75
macrs_schedules = [0,5,7]
analysis_period = 20
providers = ['federal','state','utility']
default_buildings =  [  'FastFoodRest',
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
                    'Warehouse']

def list_of_float(input):
    return [float(i) for i in input]

nested_input_definitions = {

    "Scenario": {
                "timeout_seconds":      { 'type': float,'min': 1, 'max': 295, 'default': 295},
                "user_id":              { 'type': str },
                "time_steps_per_hour":  { 'type': float, 'min': 1, 'max': 1, 'default': 1}, #aspirational - we only handle 1 timetep per hour really, this touches all of the code really


                "Site": {
                             "latitude":            { 'type': float, 'min':-180, 'max':180, 'required': True },
                             "longitude":           { 'type': float, 'min':-180, 'max':180, 'required': True },
                             "land_acres":          { 'type': float, 'min': 0, 'max': 1e6 },
                             "roof_squarefeet":     { 'type': float, 'min': 0, 'max': 1e9 },
                             "outage_start_hour":   { 'type': int, 'min': 0, 'max': 8759  },
                             "outage_end_hour":     { 'type': int , 'min': 0, 'max': 8759 },
                             "critical_load_pct":   { 'type': float, 'min': 0, 'max': 1, 'default': 0.5 },

                             "Financial":
                                    {   "om_cost_growth_pct":   { 'type': float, 'min': -1, 'max': 1, 'default': 0.025 },
                                        "escalation_pct":       { 'type': float,'min': -1, 'max': 1, 'default': 0.026  },
                                        "owner_tax_pct":        { 'type': float,'min': -1, 'max': 1 },
                                        "offtaker_tax_pct":     { 'type': float,'min': -1, 'max': 1, 'default': 0.4  },
                                        "owner_discount_pct":   { 'type': float,'min': -1, 'max': 1  },
                                        "offtaker_discount_pct":{ 'type': float,'min': -1, 'max': 1, 'default': 0.081  },
                                        "analysis_years":       { 'type': int,'min': 0, 'max': max_years, 'default': analysis_period }
                                        },

                            "LoadProfile":{
                                            "doe_reference_name":   { 'type': str, 'restrict_to':default_buildings },
                                            "annual_kwh":           { 'type': float, 'min': 0, 'max': 1e12 },
                                            "year":                 { 'type': int, 'min': 2017, 'max': 2017+max_years, 'default': 2018 },
                                            "monthly_totals_kwh":   { 'type': list_of_float },
                                            "loads_kw":             { 'type': list_of_float }
                                        },

                            "ElectricTariff": {
                                                "urdb_utilty_name":                         { 'type': str },
                                                "urdb_rate_name":                           { 'type': str },
                                                "blended_monthly_rates_us_dollars_per_kwh": { 'type': list_of_float },
                                                "monthly_demand_charges_us_dollars_per_kw": { 'type': list_of_float },
                                                "net_metering_limit_kw":                    { 'type': float,'min': 0, 'max': 1e9, 'default':0 },
                                                "interconnection_limit_kw":                 { 'type': float,'min': 0, 'max': 1e9,'default': max_big_number },
                                                "wholesale_rate_us_dollars_per_kwh":        { 'type': float, 'min': 0, 'default': 0 },
                                                "urdb_response":                            { 'type': dict },
                                                "urdb_label":                               { 'type': str }
                                        },

                            "Wind":{
                                                "min_kw":                               {  'type': float, 'min': 0, 'max': 1e9, 'default': 0  },
                                                "max_kw":                               { 'type': float, 'min': 0, 'max': 1e9, 'default': 0  },
                                                "installed_cost_us_dollars_per_kw":     { 'type': float, 'min': 0, 'max': 1e5, 'default': 2000 },
                                                "om_cost_us_dollars_per_kw":            { 'type': float, 'min': 0, 'max': 1e3, 'default': 35 },
                                                "macrs_option_years":                   { 'type': int, 'restrict_to': macrs_schedules, 'default': 5},
                                                "macrs_bonus_pct":                      { 'type': float, 'min': 0, 'max': 1, 'default': 0.5 },
                                                "federal_itc_pct":                      { 'type': float,'min': 0, 'max': 1, 'default': 0.3 },
                                                "state_ibi_pct":                        { 'type': float,'min': 0, 'max': 1, 'default': 0 },
                                                "state_ibi_max_us_dollars":             { 'type': float,'min': 0, 'max': 1e10, 'default': max_incentive },
                                                "utility_ibi_pct":                      { 'type': float,'min': 0, 'max': 1, 'default': 0 },
                                                "utility_ibi_max_us_dollars":           { 'type': float,'min': 0, 'max': 1e10, 'default': max_incentive },
                                                "federal_rebate_us_dollars_per_kw":     { 'type': float,'min': 0, 'max': 1e9, 'default': 0 },
                                                "state_rebate_us_dollars_per_kw":       { 'type': float,'min': 0, 'max': 1e9, 'default': 0 },
                                                "state_rebate_max_us_dollars":          { 'type': float,'min': 0, 'max': 1e10, 'default': max_incentive },
                                                "utility_rebate_us_dollars_per_kw":     { 'type': float,'min': 0, 'max': 1e9, 'default': 0  },
                                                "utility_rebate_max_us_dollars":        { 'type': float,'min': 0, 'max': 1e10, 'default': max_incentive },
                                                "pbi_us_dollars_per_kwh":               { 'type': float,'min': 0, 'max': 1e9, 'default': 0 },
                                                "pbi_max_us_dollars":                   { 'type': float,'min': 0, 'max': 1e9, 'default': 1e9 },
                                                "pbi_years":                            { 'type': float,'min': 0, 'max': 1e9, 'default': analysis_period },
                                                "pbi_system_max_kw":                    { 'type': float,'min': 0, 'max': 1e9, 'default': 1e9},
                                                },

                            "PV":{
                                                "min_kw":                               { 'type': float, 'min': 0, 'max': 1e9, 'default': 0  },
                                                "max_kw":                               { 'type': float, 'min': 0, 'max': 1e9, 'default': 1e9  },
                                                "installed_cost_us_dollars_per_kw":     { 'type': float, 'min': 0, 'max': 1e5, 'default': 2000 },
                                                "om_cost_us_dollars_per_kw":            { 'type': float, 'min': 0, 'max': 1e3, 'default': 16 },
                                                "degradation_pct":                      { 'type': float, 'min': 0, 'max': 1, 'default': 0.005  },
                                                "macrs_option_years":                   { 'type': int, 'restrict_to': macrs_schedules, 'default': 5 },
                                                "macrs_bonus_pct":                      { 'type': float, 'min': 0, 'max': 1, 'default': 0.5 },
                                                "federal_itc_pct":                      { 'type': float,'min': 0, 'max': 1, 'default': 0.3 },
                                                "state_ibi_pct":                        { 'type': float,'min': 0, 'max': 1, 'default': 0 },
                                                "state_ibi_max_us_dollars":             { 'type': float,'min': 0, 'max': 1e10, 'default': max_incentive },
                                                "utility_ibi_pct":                      { 'type': float,'min': 0, 'max': 1, 'default': 0 },
                                                "utility_ibi_max_us_dollars":           { 'type': float,'min': 0, 'max': 1e10, 'default':max_incentive },
                                                "federal_rebate_us_dollars_per_kw":     { 'type': float,'min': 0, 'max': 1e9, 'default': 0 },
                                                "state_rebate_us_dollars_per_kw":       { 'type': float,'min': 0, 'max': 1e9, 'default': 0 },
                                                "state_rebate_max_us_dollars":          { 'type': float,'min': 0, 'max': 1e10, 'default': max_incentive },
                                                "utility_rebate_us_dollars_per_kw":     { 'type': float,'min': 0, 'max': 1e9, 'default': 0 },
                                                "utility_rebate_max_us_dollars":        { 'type': float,'min': 0, 'max': 1e10, 'default': max_incentive },
                                                "pbi_us_dollars_per_kwh":               { 'type': float,'min': 0, 'max': 1e9, 'default': 0 },
                                                "pbi_max_us_dollars":                   { 'type': float,'min': 0, 'max': 1e9, 'default': 1e9 },
                                                "pbi_years":                            { 'type': float,'min': 0 , 'max': 1e9, 'default': analysis_period},
                                                "pbi_system_max_kw":                    { 'type': float,'min': 0, 'max': 1e9, 'default': 1e9 },
                                                "azimuth":                              { 'type': float, 'min': 0, 'max': 360, 'default': 180},
                                                "losses":                               { 'type': float,'min': 0, 'max': 0.99, 'default': 0.14 },
                                                "array_type":                           { 'type': int, 'restrict_to': [0, 1, 2, 3, 4], 'default': 0 },
                                                "module_type":                          { 'type': int, 'restrict_to': [0, 1, 2], 'default': 0 },
                                                "gcr":                                  { 'type': float, 'min': 0.01, 'max': 0.99, 'default': 0.4 },
                                                "dc_ac_ratio":                          { 'type': float, 'min': 0, 'max': 2, 'default': 1.1},
                                                "inv_eff":                              { 'type': float ,'min': 0.9, 'max': 0.995, 'default': 0.96},
                                                "radius":                               { 'type': float , 'min': 0, 'default': 0 },
                                                "tilt":                                 { 'type': float, 'min': 0, 'max': 90 }
                                                },


                            "Storage":{         "min_kw":                               { 'type': float,'min': 0, 'max': 1e9, 'default': 0 },
                                                "max_kw":                               { 'type': float,'min': 0, 'max': 1e9, 'default': 1000000 },
                                                "min_kwh":                              { 'type': float,'min': 0, 'default': 0 },
                                                "max_kwh":                              { 'type': float,'min': 0, 'default': 1000000 },
                                                "internal_efficiency_pct":              { 'type': float, 'min': 0, 'max': 1, 'default': 0.975 },
                                                "inverter_efficiency_pct":              { 'type': float, 'min': 0, 'max': 1, 'default': 0.96 },
                                                "rectifier_efficiency_pct":             { 'type': float, 'min': 0, 'max': 1, 'default': 0.96 },
                                                "soc_min_pct":                          { 'type': float, 'min': 0, 'max': 1, 'default': 0.2 },
                                                "soc_init_pct":                         { 'type': float, 'min': 0, 'max': 1, 'default': 0.5 },
                                                "canGridCharge":                        { 'type': bool, 'default': False },
                                                "installed_cost_us_dollars_per_kw":     { 'type': float,'min': 0, 'max': 1e4, 'default': 1000 },
                                                "installed_cost_us_dollars_per_kwh":    { 'type': float,'min': 0, 'max': 1e4, 'default': 500 },
                                                "replace_cost_us_dollars_per_kw":       { 'type': float, 'min': 0, 'max': 1e4, 'default': 460 },
                                                "replace_cost_us_dollars_per_kwh":      { 'type': float,'min': 0, 'max': 1e4, 'default': 230 },
                                                "inverter_replacement_year":            { 'type': float, 'min': 0, 'max': max_years, 'default': 10  },
                                                "battery_replacement_year":             { 'type': float, 'min': 0, 'max': max_years, 'default': 10  },
                                                "macrs_option_years":                   { 'type': int, 'restrict_to': macrs_schedules, 'default': 5 },
                                                "macrs_bonus_pct":                      { 'type': float, 'min': 0, 'max': 1, 'default': 0.5 },
                                                "total_itc_pct":                        { 'type': float,'min': 0, 'max': 1, 'default': 0.3 },
                                                "total_rebate_us_dollars_per_kw":       { 'type': float,'min': 0, 'max': 1e9, 'default': 0 },

                                        },

                }
    }
}
