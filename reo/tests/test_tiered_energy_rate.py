import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class TestEnergyTiers(ResourceTestCaseMixin, TestCase):
    """
    Tariff from Florida Light & Power (residential) with simple tiered energy rate:
    "energyratestructure":
    [[{"max": 1000, "rate": 0.07531, "adj": 0.0119, "unit": "kWh"}, {"rate": 0.09613, "adj": 0.0119, "unit": "kWh"}]]

    Testing with "annual_kwh": 24,000 such that the "year_one_energy_charges" should be:
        12,000 kWh * (0.07531 + 0.0119) $/kWh + 12,000 kWh * (0.09613 + 0.0119) $/kWh = $ 2,342.88
    """

    def setUp(self):
        super(TestEnergyTiers, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = {"Scenario": {"webtool_uuid": None, "description": "", "timeout_seconds": 295, "Site": {"PV": {"pbi_years": 1.0, "macrs_bonus_pct": 0.0, "max_kw": 0.0, "pbi_max_us_dollars": 1000000000.0, "radius": 0.0, "state_ibi_pct": 0.0, "state_rebate_us_dollars_per_kw": 0.0, "installed_cost_us_dollars_per_kw": 2000.0, "utility_ibi_max_us_dollars": 10000000000.0, "tilt": 0.537, "degradation_pct": 0.005, "gcr": 0.4, "pbi_system_max_kw": 1000000000.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 10000000000.0, "utility_rebate_max_us_dollars": 10000000000.0, "macrs_option_years": 5, "state_rebate_max_us_dollars": 10000000000.0, "dc_ac_ratio": 1.1, "federal_itc_pct": 0.3, "existing_kw": 0.0, "module_type": 0, "array_type": 1, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 16.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "losses": 0.14, "macrs_itc_reduction": 0.5, "federal_rebate_us_dollars_per_kw": 0.0, "inv_eff": 0.96, "azimuth": 180.0}, "Generator": {"pbi_years": 0.0, "macrs_bonus_pct": 0.0, "om_cost_us_dollars_per_kwh": 0.01, "max_kw": 1000000000.0, "pbi_max_us_dollars": 0.0, "state_ibi_pct": 0.0, "fuel_intercept_gal_per_hr": 0.0125, "generator_only_runs_during_grid_outage": True, "utility_rebate_max_us_dollars": 0.0, "installed_cost_us_dollars_per_kw": 600.0, "utility_ibi_max_us_dollars": 0.0, "fuel_avail_gal": 1000000000.0, "min_turn_down_pct": 0.0, "pbi_system_max_kw": 0.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 0.0, "diesel_fuel_cost_us_dollars_per_gallon": 3.0, "fuel_slope_gal_per_kwh": 0.068, "state_rebate_us_dollars_per_kw": 0.0, "macrs_option_years": 0, "state_rebate_max_us_dollars": 0.0, "federal_itc_pct": 0.0, "pbi_us_dollars_per_kwh": 0.0, "existing_kw": 0.0, "om_cost_us_dollars_per_kw": 10.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "macrs_itc_reduction": 0.0, "federal_rebate_us_dollars_per_kw": 0.0, "generator_sells_energy_back_to_grid": False}, "LoadProfile": {"critical_loads_kw_is_net": False, "year": 2017, "loads_kw_is_net": True, "outage_start_hour": None, "outage_end_hour": None, "monthly_totals_kwh": [], "critical_load_pct": 0.5, "loads_kw": [], "outage_is_major_event": True, "critical_loads_kw": [], "doe_reference_name": "MidriseApartment", "annual_kwh": 24000.0}, "address": "", "Storage": {"max_kwh": 0.0, "rectifier_efficiency_pct": 0.96, "total_itc_pct": 0.0, "min_kw": 0.0, "max_kw": 0.0, "replace_cost_us_dollars_per_kw": 460.0, "replace_cost_us_dollars_per_kwh": 230.0, "min_kwh": 0.0, "installed_cost_us_dollars_per_kw": 1000.0, "total_rebate_us_dollars_per_kw": 0, "installed_cost_us_dollars_per_kwh": 500.0, "inverter_efficiency_pct": 0.96, "battery_replacement_year": 10, "canGridCharge": True, "macrs_bonus_pct": 0.0, "macrs_itc_reduction": 0.5, "macrs_option_years": 7, "internal_efficiency_pct": 0.975, "soc_min_pct": 0.2, "soc_init_pct": 0.5, "inverter_replacement_year": 10}, "land_acres": None, "ElectricTariff": {"add_blended_rates_to_urdb_rate": False, "wholesale_rate_us_dollars_per_kwh": 0.0, "net_metering_limit_kw": 0.0, "interconnection_limit_kw": 100000000.0, "blended_monthly_demand_charges_us_dollars_per_kw": [], "urdb_utility_name": "Florida Power & Light Co.", "urdb_label": "", "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0, "urdb_rate_name": "RS-1 Residential Service", "urdb_response": {"sector": "Residential", "startdate": 1433116800, "phasewiring": "Single Phase", "name": "RS-1 Residential Service", "enddate": 1440975600, "source": "https://www.fpl.com/rates/pdf/electric-tariff-section8.pdf", "uri": "https://openei.org/apps/USURDB/rate/view/5550d6fd5457a3187e8b4567", "label": "5550d6fd5457a3187e8b4567", "utility": "Florida Power & Light Co.", "eiaid": 6452, "sourceparent": "https://www.fpl.com/rates.html", "energyratestructure": [[{"max": 1000, "rate": 0.07531, "adj": 0.0119, "unit": "kWh"}, {"rate": 0.09613, "adj": 0.0119, "unit": "kWh"}]], "energyweekdayschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "energyweekendschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "fixedmonthlycharge": 7.57, "energycomments": "Adjustment: Environmental, Storm Charge, Conservation, Capacity\\r\\nRate: Base rate and fuel", "supersedes": "53a455f05257a3ff4a8d8cf2", "revisions": [1431339677, 1431340059, 1431528978, 1431529815, 1431530443, 1448395688]}, "blended_annual_demand_charges_us_dollars_per_kw": 0.0, "blended_annual_rates_us_dollars_per_kwh": 0.0, "blended_monthly_rates_us_dollars_per_kwh": []}, "longitude": -91.7337, "roof_squarefeet": None, "latitude": 35.2468, "Financial": {"escalation_pct": 0.026, "offtaker_discount_pct": 0.081, "value_of_lost_load_us_dollars_per_kwh": 100.0, "analysis_years": 20, "microgrid_upgrade_cost_pct": 0.3, "offtaker_tax_pct": 0.26, "om_cost_escalation_pct": 0.025}, "Wind": {"pbi_years": 1.0, "macrs_bonus_pct": 0.0, "max_kw": 0.0, "pbi_max_us_dollars": 1000000000.0, "wind_meters_per_sec": None, "state_ibi_pct": 0.0, "utility_rebate_max_us_dollars": 10000000000.0, "installed_cost_us_dollars_per_kw": 3013.0, "utility_ibi_max_us_dollars": 10000000000.0, "pressure_atmospheres": None, "pbi_system_max_kw": 1000000000.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 10000000000.0, "wind_direction_degrees": None, "size_class": "", "state_rebate_us_dollars_per_kw": 0.0, "macrs_option_years": 5, "state_rebate_max_us_dollars": 10000000000.0, "federal_itc_pct": 0.3, "temperature_celsius": None, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 35.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "macrs_itc_reduction": 0.5, "federal_rebate_us_dollars_per_kw": 0.0}}, "time_steps_per_hour": 1, "user_uuid": None}}

    def get_response(self, data):

        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        uuid = json.loads(initial_post.content)['run_uuid']

        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
    # # the following is not needed b/c we test the app with Celery tasks in "eager" mode
    # # i.e. asynchronously. If we move to testing the API, then the while loop is needed
    # status = response['outputs']['Scenario']['status']
    # while status == "Optimizing...":
    #     time.sleep(2)
    #     response = json.loads(self.api_client.get(self.results_url + uuid).content)
    #     status = response['outputs']['Scenario']['status']

        return response

    def test_tiered_energy_rate(self):
        expected_year_one_energy_cost = 2342.88

        response = self.get_response(self.post)
        tariff_out = response['outputs']['Scenario']['Site']['ElectricTariff']
        profile_out = response['outputs']['Scenario']['Profile']
        messages = response['messages']

        try:
            self.assertEqual(tariff_out['year_one_energy_cost_us_dollars'], expected_year_one_energy_cost,
                             "Year one energy bill ({}) does not equal expected cost ({})."
                             .format(tariff_out['year_one_energy_cost_us_dollars'], expected_year_one_energy_cost))

            self.assertGreater(profile_out['pre_setup_scenario_seconds'], 0, "Profiling results failed")
            self.assertGreater(profile_out['setup_scenario_seconds'], 0, "Profiling results failed")
            self.assertGreater(profile_out['reopt_seconds'], 0, "Profiling results failed")
            self.assertGreater(profile_out['reopt_bau_seconds'], 0, "Profiling results failed")
            self.assertGreater(profile_out['parse_run_outputs_seconds'], 0, "Profiling results failed")


        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("test_tiered_energy_rate API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e
