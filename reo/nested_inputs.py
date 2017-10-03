max_years = 75
macrs_schedules = [0,5,7]
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

nested_inputs = 
{

            "Scenario": {
                        "timeout_seconds": { 'type': float,'min': 1, 'max': 295 },
                        "user_id": { 'type': str }
                        "time_steps_per_hour":{ 'type': float, 'min': 1, 'max': 1 }, #aspirational - we only handle 1 timetep per hour really, this touches all of the code really
                        },

            "Site": {
                        "latitude":{ 'type': float, 'min':-180, 'max':180 },
                        "longitude":{ 'type': float, 'min':-180, 'max':180 },
                        "land_acres":{ 'type': float, 'min': 0, 'max': 1e6 },
                        "roof_squarefeet":{ 'type': float, 'min': 0, 'max': 1e9 },
                        "outage_start_hour":{ 'type': int, 'min': 0, 'max': 8759  },
                        "outage_end_hour":{ 'type': int , 'min': 0, 'max': 8759 },
                        "critical_load_pct":{ 'type': float, 'min': 0, 'max': 1  }
                    },

            "LoadProfile":{
                            "doe_reference_name":{ 'type': str, 'restrict_to':default_buildings },
                            "annual_kwh":{ 'type': float, 'min': 0, 'max': 1e12 },
                            "year":{ 'type': int, 'min': 2017, 'max': 2017+max_years },
                            "monthly_totals_kwh":{ 'type': list_of_float },
                            "loads_kw":{ 'type': list_of_float }
                        },

            "Financial":{   "om_cost_growth_pct":{ 'type': float, 'min': -1, 'max': 1 },
                            "escalation_pct":{ 'type': float,'min': -1, 'max': 1  },
                            "owner_tax_pct":{ 'type': float,'min': -1, 'max': 1  },
                            "offtaker_tax_pct":{ 'type': float,'min': -1, 'max': 1  },
                            "owner_discount_pct":{ 'type': float,'min': -1, 'max': 1  },
                            "offtaker_discount_rate":{ 'type': float,'min': -1, 'max': 1  },
                            "analysis_years":{ 'type': int,'min': 0, 'max': max_years },
                        },

            "ElectricTariff": {
                                "urdb_utilty_name":{ 'type': str },
                                "urdb_rate_name":{ 'type': str },
                                "blended_monthly_rates_us_dollar_per_kwh":{ 'type': list_of_float },
                                "monthly_demand_charges_us_dollar_per_kw":{ 'type': list_of_float },
                                "net_metering_limit_kw":{ 'type': float,'min': 0, 'max': 1e9 },
                                "interconnection_limit_kw":{ 'type': float,'min': 0, 'max': 1e9 },
                                "wholesale_rate_us_dollar_per_kwh":{ 'type': float, 'min': 0 },
                                "urdb_response":{ 'type': dict },
                                "urdb_label":{ 'type': str }
                        },

              "Wind":{
                                "min_kw":{  'type': float, 'min': 0, 'max': 1e9  },
                                "max_kw":{ 'type': float, 'min': 0, 'max': 1e9  },
                                "installed_cost_us_dollar_per_kw":{ 'type': float, 'min': 0, 'max': 1e5 },
                                "om_cost_us_dollar_per_kw":{ 'type': float, 'min': 0, 'max': 1e3 },
                                "macrs_option_years":{ 'type': int, 'restrict_to': macrs_schedules},
                                "macrs_bonus_pct":{ 'type': float, 'min': 0, 'max': 1 },
                                "macrs_itc_reduction_pct":{ 'type': float, 'min': 0, 'max': 1 },
                                "federal_itc_pct": { 'type': float,'min': 0, 'max': 1 },
                                "state_ibi_pct": { 'type': float,'min': 0, 'max': 1 },
                                "state_ibi_max_pct": { 'type': float,'min': 0, 'max': 1 },
                                "utility_ibi_pct": { 'type': float,'min': 0, 'max': 1 },
                                "utility_ibi_max_pct": { 'type': float,'min': 0, 'max': 1 },
                                "federal_rebate_us_dollar_per_kw": { 'type': float,'min': 0, 'max': 1 },
                                "state_rebate_us_dollar_per_kw": { 'type': float,'min': 0, 'max': 1 },
                                "state_rebate_max_us_dollar_per_kw": { 'type': float,'min': 0, 'max': 1 },
                                "utility_rebate_us_dollar_per_kw": { 'type': float,'min': 0, 'max': 1 },
                                "state_rebate_max_us_dollar_per_kw": { 'type': float,'min': 0, 'max': 1 },
                                "pbi_us_dollars_per_kwh": { 'type': float,'min': 0, 'max': 1 },
                                "pbi_max_us_dollars": { 'type': float,'min': 0, 'max': 1 },
                                "pbi_years": { 'type': float,'min': 0, 'max': 1 },
                                "pbi_system_max_kw": { 'type': float,'min': 0, 'max': 1 },
                                },

            "PV":{
                                "min_kw":{  'type': float, 'min': 0, 'max': 1e9  },
                                "max_kw":{ 'type': float, 'min': 0, 'max': 1e9  },
                                "installed_cost_us_dollar_per_kw":{ 'type': float, 'min': 0, 'max': 1e5 },
                                "om_cost_us_dollar_per_kw":{ 'type': float, 'min': 0, 'max': 1e3 },
                                "degradation_pct":{ 'type': float, 'min': 0, 'max': 1 },
                                "macrs_option_years":{ 'type': int, 'restrict_to': macrs_schedules},
                                "macrs_bonus_pct":{ 'type': float, 'min': 0, 'max': 1 },
                                "macrs_itc_reduction_pct":{ 'type': float, 'min': 0, 'max': 1 },
                                "federal_itc_pct": { 'type': float,'min': 0, 'max': 1 },
                                "state_ibi_pct": { 'type': float,'min': 0, 'max': 1 },
                                "state_ibi_max_pct": { 'type': float,'min': 0, 'max': 1 },
                                "utility_ibi_pct": { 'type': float,'min': 0, 'max': 1 },
                                "utility_ibi_max_pct": { 'type': float,'min': 0, 'max': 1 },
                                "federal_rebate_us_dollar_per_kw": { 'type': float,'min': 0, 'max': 1 },
                                "state_rebate_us_dollar_per_kw": { 'type': float,'min': 0, 'max': 1 },
                                "state_rebate_max_us_dollar_per_kw": { 'type': float,'min': 0, 'max': 1 },
                                "utility_rebate_us_dollar_per_kw": { 'type': float,'min': 0, 'max': 1 },
                                "state_rebate_max_us_dollar_per_kw": { 'type': float,'min': 0, 'max': 1 },
                                "pbi_us_dollars_per_kwh": { 'type': float,'min': 0, 'max': 1 },
                                "pbi_max_us_dollars": { 'type': float,'min': 0, 'max': 1 },
                                "pbi_years": { 'type': float,'min': 0, 'max': 1 },
                                "pbi_system_max_kw": { 'type': float,'min': 0, 'max': 1 },
                                },


            "PVWatt":{
                                "azimuth": { 'type': float, 'min': 0, 'max': 360},
                                "losses": { 'type': float,'min': 0, 'max': 0.99 },
                                "array_type": { 'type': int, 'restrict_to': [0, 1, 2, 3, 4] },
                                "module_type": { 'type': int, 'restrict_to': [0, 1, 2] },
                                "gcr": { 'type': float, 'min': 0.01, 'max': 0.99 },
                                "dc_ac_ratio": { 'type': float, 'min': 0, 'max': 2},
                                "inv_eff": { 'type': float ,'min': 0.9, 'max': 0.995},
                                "radius": { 'type': float , 'min': 0 },
                                "tilt": { 'type': float, 'min': 0, 'max': 90 }
                    },

            "Storage":{         "min_kw": { 'type': float,'min': 0, 'max': 1e9 },
                                "max_kw": { 'type': float,'min': 0, 'max': 1e9 },
                                "min_kwh": { 'type': float,'min': 0 },
                                "max_kwh": { 'type': float,'min': 0 },
                                "internal_efficiency_pct": { 'type': float, 'min': 0, 'max': 1 },
                                "inverter_efficiency_pct": { 'type': float, 'min': 0, 'max': 1 },
                                "rectifier_efficiency_pct": { 'type': float, 'min': 0, 'max': 1 },
                                "soc_min_pct": { 'type': float, 'min': 0, 'max': 1 },
                                "soc_init_pct": { 'type': float, 'min': 0, 'max': 1 },
                                "canGridCharge": { 'type': bool },
                                "installed_cost_us_dollar_per_kw": { 'type': float,'min': 0, 'max': 1e4 },
                                "installed_cost_us_dollar_per_kwh": { 'type': float,'min': 0, 'max': 1e4 },
                                "replace_cost_us_dollar_per_kw": { 'type': float, 'min': 0, 'max': 1e4 },
                                "replace_cost_us_dollar_per_kwh": { 'type': float,'min': 0, 'max': 1e4 },
                                "inverter_replacement_year": { 'type': float, 'min': 0, 'max': max_years  },
                                "battery_replacement_year": { 'type': float, 'min': 0, 'max': max_years  },
                                "macrs_option_years":{ 'type': int, 'restrict_to': macrs_schedules},
                                "macrs_bonus_pct":{ 'type': float, 'min': 0, 'max': 1 },
                                "macrs_itc_reduction_pct":{ 'type': float, 'min': 0, 'max': 1 }
                                "total_itc_pct": { 'type': float,'min': 0, 'max': 1 },
                                "total_rebate_us_dollar_per_kw": { 'type': float,'min': 0, 'max': 1 },
                                  
                        },

        }
