import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class TestHybridLoadProfile(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        """
        Testing electric hybrid load profile funtionality where `annual_kwh` and
        'doe_reference` are sent as list inputs with `percent_share` for calculating
        weighted average based hybrid load profile
        """
        super(TestHybridLoadProfile, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = {
            "Scenario": {
                "Site": {
                    "latitude": 47.6062,
                    "longitude": -122.3321,
                    "address": "Seattle WA",
                    "land_acres": 0.925,
                    "roof_squarefeet": 1000.0,
                    "Financial": {
                        "om_cost_escalation_pct": 0.025,
                        "escalation_pct": 0.023,
                        "offtaker_tax_pct": 0.26,
                        "offtaker_discount_pct": 0.083,
                        "analysis_years": 25.0,
                        "value_of_lost_load_us_dollars_per_kwh": 100.0,
                        "microgrid_upgrade_cost_pct": 0.3
                    },
                    "LoadProfile": {
                        "percent_share":[20.0,20.0,20.0,20.0,20.0,],
                        "doe_reference_name":["RetailStore","LargeOffice",
                                               "MediumOffice","SmallOffice",
                                               "Warehouse"],
                        "annual_kwh": 500000.0,
                        "year": 2017,
                        "monthly_totals_kwh": [],
                        "loads_kw": [],
                        "critical_loads_kw": [],
                        "loads_kw_is_net": True,
                        "critical_loads_kw_is_net": False,
                        "outage_start_hour": None,
                        "outage_end_hour": None,
                        "critical_load_pct": 0.5,
                        "outage_is_major_event": True
                    },
                    "ElectricTariff": {
                        "urdb_utility_name": "",
                        "urdb_rate_name": "",
                        "add_blended_rates_to_urdb_rate": False,
                        "blended_annual_rates_us_dollars_per_kwh": 0.3,
                        "blended_annual_demand_charges_us_dollars_per_kw": 20.0,
                        "net_metering_limit_kw": 0.0,
                        "interconnection_limit_kw": 100000000.0,
                        "urdb_response": None,
                        "urdb_label": ""
                    },
                    "Wind": {
                        "size_class": "",
                        "wind_meters_per_sec": None,
                        "wind_direction_degrees": None,
                        "temperature_celsius": None,
                        "pressure_atmospheres": None,
                        "min_kw": 0.0,
                        "max_kw": 0.0,
                        "installed_cost_us_dollars_per_kw": 3013.0,
                        "om_cost_us_dollars_per_kw": 40.0,
                        "macrs_option_years": 5,
                        "macrs_bonus_pct": 1.0,
                        "macrs_itc_reduction": 0.5,
                        "federal_itc_pct": 0.26,
                        "state_ibi_pct": 0.0,
                        "state_ibi_max_us_dollars": 10000000000.0,
                        "utility_ibi_pct": 0.0,
                        "utility_ibi_max_us_dollars": 10000000000.0,
                        "federal_rebate_us_dollars_per_kw": 0.0,
                        "state_rebate_us_dollars_per_kw": 0.0,
                        "state_rebate_max_us_dollars": 10000000000.0,
                        "utility_rebate_us_dollars_per_kw": 0.0,
                        "utility_rebate_max_us_dollars": 10000000000.0,
                        "pbi_us_dollars_per_kwh": 0.0,
                        "pbi_max_us_dollars": 1000000000.0,
                        "pbi_years": 1.0,
                        "pbi_system_max_kw": 1000000000.0
                    },
                    "PV": {
                            "pv_name": "ground",
                            "existing_kw": 0.0,
                            "min_kw": 10.0,
                            "max_kw": 10.0,
                            "installed_cost_us_dollars_per_kw": 1600.0,
                            "om_cost_us_dollars_per_kw": 16.0,
                            "macrs_option_years": 5,
                            "macrs_bonus_pct": 1.0,
                            "macrs_itc_reduction": 0.5,
                            "federal_itc_pct": 0.26,
                            "state_ibi_pct": 0.0,
                            "state_ibi_max_us_dollars": 10000000000.0,
                            "utility_ibi_pct": 0.0,
                            "utility_ibi_max_us_dollars": 10000000000.0,
                            "federal_rebate_us_dollars_per_kw": 0.0,
                            "state_rebate_us_dollars_per_kw": 0.0,
                            "state_rebate_max_us_dollars": 10000000000.0,
                            "utility_rebate_us_dollars_per_kw": 0.0,
                            "utility_rebate_max_us_dollars": 10000000000.0,
                            "pbi_us_dollars_per_kwh": 0.0,
                            "pbi_max_us_dollars": 1000000000.0,
                            "pbi_years": 1.0,
                            "pbi_system_max_kw": 1000000000.0,
                            "degradation_pct": 0.005,
                            "azimuth": 180.0,
                            "losses": 0.14,
                            "array_type": 0,
                            "module_type": 0,
                            "gcr": 0.4,
                            "dc_ac_ratio": 1.2,
                            "inv_eff": 0.96,
                            "radius": 0.0,
                            "tilt": 34.5794343,
                            "location": "ground"
                        },
                    "Storage": {
                        "min_kw": 0.0,
                        "max_kw": 0.0,
                        "min_kwh": 0.0,
                        "max_kwh": 1000000.0,
                        "internal_efficiency_pct": 0.975,
                        "inverter_efficiency_pct": 0.96,
                        "rectifier_efficiency_pct": 0.96,
                        "soc_min_pct": 0.2,
                        "soc_init_pct": 0.5,
                        "canGridCharge": True,
                        "installed_cost_us_dollars_per_kw": 840.0,
                        "installed_cost_us_dollars_per_kwh": 420.0,
                        "replace_cost_us_dollars_per_kw": 410.0,
                        "replace_cost_us_dollars_per_kwh": 200.0,
                        "inverter_replacement_year": 10,
                        "battery_replacement_year": 10,
                        "macrs_option_years": 7,
                        "macrs_bonus_pct": 1.0,
                        "macrs_itc_reduction": 0.5,
                        "total_itc_pct": 0.0,
                        "total_rebate_us_dollars_per_kw": 0
                    },
                    "Generator": {
                        "existing_kw": 0.0,
                        "min_kw": 0.0,
                        "max_kw": 0.0,
                        "installed_cost_us_dollars_per_kw": 500.0,
                        "om_cost_us_dollars_per_kw": 10.0,
                        "om_cost_us_dollars_per_kwh": 0.0,
                        "diesel_fuel_cost_us_dollars_per_gallon": 3.0,
                        "fuel_slope_gal_per_kwh": 0.076,
                        "fuel_intercept_gal_per_hr": 0.0,
                        "fuel_avail_gal": 660.0,
                        "min_turn_down_pct": 0.0,
                        "generator_only_runs_during_grid_outage": True,
                        "generator_sells_energy_back_to_grid": False,
                        "macrs_option_years": 0,
                        "macrs_bonus_pct": 1.0,
                        "macrs_itc_reduction": 0.0,
                        "federal_itc_pct": 0.0,
                        "state_ibi_pct": 0.0,
                        "state_ibi_max_us_dollars": 0.0,
                        "utility_ibi_pct": 0.0,
                        "utility_ibi_max_us_dollars": 0.0,
                        "federal_rebate_us_dollars_per_kw": 0.0,
                        "state_rebate_us_dollars_per_kw": 0.0,
                        "state_rebate_max_us_dollars": 0.0,
                        "utility_rebate_us_dollars_per_kw": 0.0,
                        "utility_rebate_max_us_dollars": 0.0,
                        "pbi_us_dollars_per_kwh": 0.0,
                        "pbi_max_us_dollars": 0.0,
                        "pbi_years": 0.0,
                        "pbi_system_max_kw": 0.0
                    }
                },
                "timeout_seconds": 295,
                "user_uuid": None,
                "description": "",
                "time_steps_per_hour": 1,
                "webtool_uuid": None
            }
        }

    def test_hybrid_loadprofile(self):
        resp = self.api_client.post(self.submit_url, format='json', data=self.post)
        uuid = json.loads(resp.content)['run_uuid']
        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
        lp = response['outputs']['Scenario']['Site']['LoadProfile']
        resultant_load_profile = lp["year_one_electric_load_series_kw"]

        resultant_hybrid_annual_kwh = lp["annual_calculated_kwh"]

# this comparison of the 'resultant_load_profile' and 'manually_calculated_load_profile' is possible because there is no existing-pv in this case. If existing-pv is present, then the resultant_hybrid_annual_kwh would be different when net native load is calculated by subtracting existing-pv's output.

        self.assertAlmostEquals(resultant_hybrid_annual_kwh, 500000x s, places=2)