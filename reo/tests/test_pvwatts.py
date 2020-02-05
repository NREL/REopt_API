import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.src.pvwatts import PVWatts
import logging
logging.disable(logging.CRITICAL)


class TestPVWatts(ResourceTestCaseMixin, TestCase):
    def setUp(self):
        super(TestPVWatts, self).setUp()
        self.pvwatts_denver = PVWatts(latitude=39.7392, longitude=-104.99, tilt=40)
        self.pvwatts_zimbabwe = PVWatts(latitude=-19.0154, longitude=29.1549, tilt=20)
        self.pvwatts_southafrica = PVWatts(latitude=-26.2041, longitude=28.0473, tilt=20)

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        uuid = json.loads(initial_post.content)['run_uuid']
        response = self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid)))

        return response
    
    def test_pvwatts(self):

        denver_data = self.pvwatts_denver.data
        self.assertAlmostEqual(denver_data['outputs']['ac_annual'], 1677, places=0)
        self.assertEquals(len(denver_data['outputs']['ac']), 8760)
        self.assertEquals(denver_data['station_info']['solar_resource_file'], 'W10498N3973.csv')
        self.assertEquals(denver_data['station_info']['distance'], 1335)

        zimbabwe_data = self.pvwatts_zimbabwe.data
        self.assertAlmostEqual(zimbabwe_data['outputs']['ac_annual'], 1319, places=0)
        self.assertEquals(len(zimbabwe_data['outputs']['ac']), 8760)

        sa_data = self.pvwatts_southafrica.data
        self.assertAlmostEqual(sa_data['outputs']['ac_annual'], 1243, places=0)
        self.assertEquals(len(sa_data['outputs']['ac']), 8760)

    def test_international(self):
        post = {"Scenario": {"webtool_uuid": None, "description": "", "timeout_seconds": 295, 
        "Site": {
          "PV": {"pbi_years": 1.0, "macrs_bonus_pct": 0.0, "max_kw": 100.0, "pbi_max_us_dollars": 1000000000.0, "radius": 100.0, "state_ibi_pct": 0.0, "state_rebate_us_dollars_per_kw": 0.0, "installed_cost_us_dollars_per_kw": 2000.0, "utility_ibi_max_us_dollars": 10000000000.0, "tilt": 35.2468, "degradation_pct": 0.005, "gcr": 0.4, "pbi_system_max_kw": 1000000000.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 10000000000.0, "utility_rebate_max_us_dollars": 10000000000.0, "macrs_option_years": 5, "state_rebate_max_us_dollars": 10000000000.0, "dc_ac_ratio": 1.1, "federal_itc_pct": 0.3, "existing_kw": 0.0, "module_type": 0, "array_type": 0, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 16.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "losses": 0.14, "macrs_itc_reduction": 0.5, "federal_rebate_us_dollars_per_kw": 0.0, "inv_eff": 0.96, "azimuth": 180.0}, 
          "Generator": {"pbi_years": 0.0, "macrs_bonus_pct": 0.0, "om_cost_us_dollars_per_kwh": 0.01, "max_kw": 1000000000.0, "pbi_max_us_dollars": 0.0, "state_ibi_pct": 0.0, "fuel_intercept_gal_per_hr": 0.0125, "generator_only_runs_during_grid_outage": True, "utility_rebate_max_us_dollars": 0.0, "installed_cost_us_dollars_per_kw": 600.0, "utility_ibi_max_us_dollars": 0.0, "fuel_avail_gal": 1000000000.0, "min_turn_down_pct": 0.0, "pbi_system_max_kw": 0.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 0.0, "diesel_fuel_cost_us_dollars_per_gallon": 3.0, "fuel_slope_gal_per_kwh": 0.068, "state_rebate_us_dollars_per_kw": 0.0, "macrs_option_years": 0, "state_rebate_max_us_dollars": 0.0, "federal_itc_pct": 0.0, "pbi_us_dollars_per_kwh": 0.0, "existing_kw": 0.0, "om_cost_us_dollars_per_kw": 10.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "macrs_itc_reduction": 0.0, "federal_rebate_us_dollars_per_kw": 0.0, "generator_sells_energy_back_to_grid": False}, 
          "LoadProfile": {"critical_loads_kw_is_net": False, "year": 2017, "loads_kw_is_net": True, "outage_start_hour": None, "outage_end_hour": None, "monthly_totals_kwh": [], "critical_load_pct": 0.5, "outage_is_major_event": True, "critical_loads_kw": [], "doe_reference_name": "MidriseApartment", "annual_kwh": None}, 
          "address": "", 
          "Storage": {"max_kwh": 0.0, "rectifier_efficiency_pct": 0.96, "total_itc_pct": 0.0, "min_kw": 0.0, "max_kw": 0.0, "replace_cost_us_dollars_per_kw": 460.0, "replace_cost_us_dollars_per_kwh": 230.0, "min_kwh": 0.0, "installed_cost_us_dollars_per_kw": 1000.0, "total_rebate_us_dollars_per_kw": 0, "installed_cost_us_dollars_per_kwh": 500.0, "inverter_efficiency_pct": 0.96, "battery_replacement_year": 10, "canGridCharge": True, "macrs_bonus_pct": 0.0, "macrs_itc_reduction": 0.5, "macrs_option_years": 7, "internal_efficiency_pct": 0.975, "soc_min_pct": 0.2, "soc_init_pct": 0.5, "inverter_replacement_year": 10}, 
          "land_acres": None, 
          "ElectricTariff": {"add_blended_rates_to_urdb_rate": False, "wholesale_rate_us_dollars_per_kwh": 0.0, "net_metering_limit_kw": 0.0, "interconnection_limit_kw": 100000000.0, "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "urdb_utility_name": "", "urdb_label": "", "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0, "urdb_rate_name": "", "urdb_response": None, "blended_annual_demand_charges_us_dollars_per_kw": 0.0, "blended_annual_rates_us_dollars_per_kwh": 0.0, "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]}, 
          "longitude": -59.5236, 
          "roof_squarefeet": None, 
          "latitude": -54.7962, 
          "Financial": {"escalation_pct": 0.026, "offtaker_discount_pct": 0.081, "value_of_lost_load_us_dollars_per_kwh": 100.0, "analysis_years": 20, "microgrid_upgrade_cost_pct": 0.3, "offtaker_tax_pct": 0.26, "om_cost_escalation_pct": 0.025}, "Wind": {"pbi_years": 1.0, "macrs_bonus_pct": 0.0, "max_kw": 0.0, "pbi_max_us_dollars": 1000000000.0, "wind_meters_per_sec": None, "state_ibi_pct": 0.0, "utility_rebate_max_us_dollars": 10000000000.0, "installed_cost_us_dollars_per_kw": 3013.0, "utility_ibi_max_us_dollars": 10000000000.0, "pressure_atmospheres": None, "pbi_system_max_kw": 1000000000.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 10000000000.0, "wind_direction_degrees": None, "size_class": "", "state_rebate_us_dollars_per_kw": 0.0, "macrs_option_years": 5, "state_rebate_max_us_dollars": 10000000000.0, "federal_itc_pct": 0.3, "temperature_celsius": None, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 35.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "macrs_itc_reduction": 0.5, "federal_rebate_us_dollars_per_kw": 0.0}}, 
          "time_steps_per_hour": 1, "user_uuid": None}}
        
        response = self.get_response(post)
        self.assertTrue('PV Watts could not locate a dataset station within the search radius' in str(response.content))