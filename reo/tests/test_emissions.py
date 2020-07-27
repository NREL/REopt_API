import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from unittest import skip


class ClassAttributes:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)


class TestEmissions(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestEmissions, self).setUp()

        self.emissions_url = '/v1/emissions_profile'
        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = {
          "Scenario": {
            "webtool_uuid": None,
            "description": "",
            "timeout_seconds": 295,
            "Site": {
              "PV": {
                "pbi_years": 1.0,
                "macrs_bonus_pct": 0.0,
                "max_kw": 10000000.0,
                "pbi_max_us_dollars": 1000000000.0,
                "radius": 0.0,
                "state_ibi_pct": 0.0,
                "state_rebate_us_dollars_per_kw": 0.0,
                "installed_cost_us_dollars_per_kw": 2000.0,
                "utility_ibi_max_us_dollars": 10000000000.0,
                "tilt": 10.0,
                "degradation_pct": 0.005,
                "gcr": 0.4,
                "pbi_system_max_kw": 1000000000.0,
                "utility_ibi_pct": 0.0,
                "state_ibi_max_us_dollars": 10000000000.0,
                "utility_rebate_max_us_dollars": 10000000000.0,
                "macrs_option_years": 5,
                "state_rebate_max_us_dollars": 10000000000.0,
                "dc_ac_ratio": 1.1,
                "federal_itc_pct": 0.3,
                "existing_kw": 0.0,
                "module_type": 0,
                "array_type": 1,
                "pbi_us_dollars_per_kwh": 0.0,
                "om_cost_us_dollars_per_kw": 16.0,
                "utility_rebate_us_dollars_per_kw": 0.0,
                "min_kw": 0.0,
                "losses": 0.14,
                "macrs_itc_reduction": 0.5,
                "federal_rebate_us_dollars_per_kw": 0.0,
                "inv_eff": 0.96,
                "azimuth": 180.0
              },
              "Generator": {
                "pbi_years": 0.0,
                "macrs_bonus_pct": 0.0,
                "om_cost_us_dollars_per_kwh": 0.01,
                "max_kw": 10000000.0,
                "pbi_max_us_dollars": 0.0,
                "state_ibi_pct": 0.0,
                "fuel_intercept_gal_per_hr": 0.0,
                "generator_only_runs_during_grid_outage": True,
                "utility_rebate_max_us_dollars": 0.0,
                "installed_cost_us_dollars_per_kw": 600.0,
                "utility_ibi_max_us_dollars": 0.0,
                "fuel_avail_gal": 1000000000.0,
                "min_turn_down_pct": 0.0,
                "pbi_system_max_kw": 0.0,
                "utility_ibi_pct": 0.0,
                "state_ibi_max_us_dollars": 0.0,
                "diesel_fuel_cost_us_dollars_per_gallon": 0.99,
                "fuel_slope_gal_per_kwh": 0.0,
                "state_rebate_us_dollars_per_kw": 0.0,
                "macrs_option_years": 0,
                "state_rebate_max_us_dollars": 0.0,
                "federal_itc_pct": 0.0,
                "pbi_us_dollars_per_kwh": 0.0,
                "existing_kw": 0.0,
                "om_cost_us_dollars_per_kw": 10.0,
                "utility_rebate_us_dollars_per_kw": 0.0,
                "min_kw": 1.0,
                "macrs_itc_reduction": 0.0,
                "federal_rebate_us_dollars_per_kw": 0.0,
                "generator_sells_energy_back_to_grid": False
              },
              "LoadProfile": {
                "critical_loads_kw_is_net": False,
                "year": 2017,
                "loads_kw_is_net": True,
                "outage_start_hour": 180,
                "outage_end_hour": 190,
                "monthly_totals_kwh": [],
                "critical_load_pct": 0.5,
                "loads_kw": [],
                "outage_is_major_event": True,
                "critical_loads_kw": [],
                "doe_reference_name": "MidriseApartment",
                "annual_kwh": 259525.0
              },
              "address": "",
              "Storage": {
                "max_kwh": 0.0,
                "rectifier_efficiency_pct": 0.96,
                "total_itc_pct": 0.0,
                "min_kw": 0.0,
                "max_kw": 0.0,
                "replace_cost_us_dollars_per_kw": 460.0,
                "replace_cost_us_dollars_per_kwh": 230.0,
                "min_kwh": 0.0,
                "installed_cost_us_dollars_per_kw": 1000.0,
                "total_rebate_us_dollars_per_kw": 0,
                "installed_cost_us_dollars_per_kwh": 500.0,
                "inverter_efficiency_pct": 0.96,
                "battery_replacement_year": 10,
                "canGridCharge": True,
                "macrs_bonus_pct": 0.0,
                "macrs_itc_reduction": 0.5,
                "macrs_option_years": 7,
                "internal_efficiency_pct": 0.975,
                "soc_min_pct": 0.2,
                "soc_init_pct": 0.5,
                "inverter_replacement_year": 10
              },
              "land_acres": None,
              "ElectricTariff": {
                "add_blended_rates_to_urdb_rate": False,
                "wholesale_rate_us_dollars_per_kwh": 0.0,
                "net_metering_limit_kw": 0.0,
                "interconnection_limit_kw": 100000000.0,
                "blended_monthly_demand_charges_us_dollars_per_kw": [],
                "urdb_utility_name": "",
                "urdb_label": "",
                "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0,
                "urdb_rate_name": "custom",
                "urdb_response": None,
                "blended_monthly_rates_us_dollars_per_kwh": [0.27, .27, 0.21, 0.23, 0.27, 0.19, 0.22, 0.17, 0.24, 0.26, 0.18, 0.2],
                "blended_monthly_demand_charges_us_dollars_per_kw": [10.08, 10.11, 10, 10, 10.15, 10.14, 10.09, 10.06, 10, 10, 10.05, 10]
              },
              "longitude": -91.7337,
              "roof_squarefeet": None,
              "latitude": 35.2468,
              "Financial": {
                "escalation_pct": 0.026,
                "offtaker_discount_pct": 0.081,
                "value_of_lost_load_us_dollars_per_kwh": 100.0,
                "analysis_years": 20,
                "microgrid_upgrade_cost_pct": 0.3,
                "offtaker_tax_pct": 0.26,
                "om_cost_escalation_pct": 0.025
              },
              "Wind": {
                "pbi_years": 1.0,
                "macrs_bonus_pct": 0.0,
                "max_kw": 0.0,
                "pbi_max_us_dollars": 1000000000.0,
                "wind_meters_per_sec": None,
                "state_ibi_pct": 0.0,
                "utility_rebate_max_us_dollars": 10000000000.0,
                "installed_cost_us_dollars_per_kw": 3013.0,
                "utility_ibi_max_us_dollars": 10000000000.0,
                "pressure_atmospheres": None,
                "pbi_system_max_kw": 1000000000.0,
                "utility_ibi_pct": 0.0,
                "state_ibi_max_us_dollars": 10000000000.0,
                "wind_direction_degrees": None,
                "size_class": "",
                "state_rebate_us_dollars_per_kw": 0.0,
                "macrs_option_years": 5,
                "state_rebate_max_us_dollars": 10000000000.0,
                "federal_itc_pct": 0.3,
                "temperature_celsius": None,
                "pbi_us_dollars_per_kwh": 0.0,
                "om_cost_us_dollars_per_kw": 35.0,
                "utility_rebate_us_dollars_per_kw": 0.0,
                "min_kw": 0.0,
                "macrs_itc_reduction": 0.5,
                "federal_rebate_us_dollars_per_kw": 0.0
              }
            },
            "time_steps_per_hour": 1,
            "user_uuid": None
          }
        }

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        uuid = json.loads(initial_post.content)['run_uuid']
        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
        return response

    def test_emissions_profile_url(self):
        test = self.api_client.get('/v1/emissions_profile/',data={"latitude":60.27641,"longitude":-144.81502})
        self.assertTrue(json.loads(test.content)['region_abbr'] == 'AK')

        test = self.api_client.get('/v1/emissions_profile/',data={"latitude":21.55329,"longitude":-158.014155})
        self.assertTrue(json.loads(test.content)['region_abbr'] == 'HI-Oahu')

        test = self.api_client.get('/v1/emissions_profile/',data={"latitude":21.97966,"longitude":-159.553226})
        self.assertTrue(json.loads(test.content)['region_abbr'] == 'HI')

        test = self.api_client.get('/v1/emissions_profile/',data={"latitude":45,"longitude":-110})
        self.assertTrue(json.loads(test.content)['region_abbr'] == 'NW')
        
        test = self.api_client.get('/v1/emissions_profile/',data={"latitude":1,"longitude":1})
        self.assertTrue("Your site location (1.0,1.0) is more than 5 miles from the nearest emission region." in str(test.content))

    def test_bad_grid_emissions_profile(self):
        """
        Tests that a poorly formatted utility emissions factor profile does not validate 
        and the optimization does not start
        """
        data = self.post
        data['Scenario']['Site']['ElectricTariff']['emissions_factor_series_lb_CO2_per_kwh'] = [1,2]

        response = json.loads(self.api_client.post(self.submit_url, format='json', data=data).content)

        self.assertTrue('emissions_factor_series_lb_CO2_per_kwh' in response['messages']['input_errors'][0])

    def test_bad_grid_emissions_profile_location(self):
        """
        Tests that a location 5 miles outside the AVERT boundaries does not return an emission
        factor profile - optimization is not stopped and emissions are not calculated
        """
        data = self.post
        data['Scenario']['Site']['latitude'] = 1
        data['Scenario']['Site']['longitude'] = 1

        response = self.get_response(data)

        text_to_check = "'Emissons Warning': {'error': 'Your site location (1.0,1.0) is more than 5 miles from the nearest emission region. Cannot calculate emissions.'"

        self.assertTrue(text_to_check in response['messages']['warnings'])
        self.assertTrue(response['outputs']['Scenario']['Site']['year_one_emissions_lb_C02'] is None)
        self.assertTrue(response['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_C02'] is None)
        self.assertTrue(round(response['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_C02'],-1) ==150)