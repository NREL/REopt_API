import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class TestPVWindProdFactor(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestPVWindProdFactor, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = {"Scenario": {"webtool_uuid": None, "description": "", "timeout_seconds": 295, 
        "Site": {
          "PV": {"prod_factor_series_kw": [1]*8760, "min_kw": 2.0, "max_kw": 2.0, "existing_kw": 0.0, "pbi_years": 1.0, "macrs_bonus_pct": 0.0, "pbi_max_us_dollars": 1000000000.0, "radius": 0.0, "state_ibi_pct": 0.0, "state_rebate_us_dollars_per_kw": 0.0, "installed_cost_us_dollars_per_kw": 2000.0, "utility_ibi_max_us_dollars": 10000000000.0, "tilt": 35.2468, "degradation_pct": 0.005, "gcr": 0.4, "pbi_system_max_kw": 1000000000.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 10000000000.0, "utility_rebate_max_us_dollars": 10000000000.0, "macrs_option_years": 5, "state_rebate_max_us_dollars": 10000000000.0, "dc_ac_ratio": 1.1, "federal_itc_pct": 0.3, "module_type": 0, "array_type": 0, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 16.0, "utility_rebate_us_dollars_per_kw": 0.0, "losses": 0.14, "macrs_itc_reduction": 0.5, "federal_rebate_us_dollars_per_kw": 0.0, "inv_eff": 0.96, "azimuth": 180.0},
          "Wind": {"prod_factor_series_kw": [1]*8760, "min_kw": 2, "max_kw": 2, "installed_cost_us_dollars_per_kw": 0.0, "om_cost_us_dollars_per_kw": 0},
          "Generator": {"max_kw": 0.0},
          "LoadProfile": {"doe_reference_name": "MidriseApartment", "annual_kwh": None, "critical_loads_kw_is_net": False, "year": 2017, "loads_kw_is_net": True, "outage_start_time_step": None, "outage_end_time_step": None, "monthly_totals_kwh": [], "critical_load_pct": 0.5, "outage_is_major_event": True, "critical_loads_kw": []},
          "address": "", 
          "Storage": {"max_kwh": 0.0, "max_kw": 0.0},
          "land_acres": None, 
          "ElectricTariff": {"add_blended_rates_to_urdb_rate": False, "wholesale_rate_us_dollars_per_kwh": 0.0, "net_metering_limit_kw": 0.0, "interconnection_limit_kw": 100000000.0, "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "urdb_utility_name": "", "urdb_label": "", "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0, "urdb_rate_name": "", "urdb_response": None, "blended_annual_demand_charges_us_dollars_per_kw": 0.0, "blended_annual_rates_us_dollars_per_kwh": 0.0, "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]}, 
          "longitude": -91.7337, 
          "roof_squarefeet": None, 
          "latitude": 35.2468, 
          "Financial": {"escalation_pct": 0.026, "offtaker_discount_pct": 0.081, "value_of_lost_load_us_dollars_per_kwh": 100.0, "analysis_years": 20, "microgrid_upgrade_cost_pct": 0.3, "offtaker_tax_pct": 0.26, "om_cost_escalation_pct": 0.025},
          }, 
          "time_steps_per_hour": 1, "user_uuid": None}}

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        uuid = json.loads(initial_post.content)['run_uuid']
        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
        return response

    def test_custom_prod_factors(self):
        """
        Pass in a PV and Wind each with min_kw and max_kw constraints set to 2 kW. 
        Set each prod_factor_series_kw to [1]*8760 and then expect the year_one_energy_produced_kwh to be 2 * 8760. 
        Tests the the custom prod_factor is being used, not one one from PV Watts or the Wind SAM Sdk
        """
        response = self.get_response(self.post)
        pv_out = response['outputs']['Scenario']['Site']['PV']
        wind_out = response['outputs']['Scenario']['Site']['Wind']

        self.assertEqual(pv_out['size_kw'], 2,
                         "PV size ({} kW) does not equal expected value ({} kW)."
                         .format(pv_out['size_kw'], 2))
        self.assertEqual(pv_out['year_one_energy_produced_kwh'], 2 * 8760,
                         "PV energy produced ({} kWh) does not equal expected value({} kWh)."
                         .format(pv_out['year_one_energy_produced_kwh'], 2 * 8760))
        self.assertEqual(wind_out['size_kw'], 2,
                         "Wind size ({} kW) does not equal expected value ({} kW)."
                         .format(wind_out['size_kw'], 2))
        self.assertEqual(wind_out['year_one_energy_produced_kwh'], 2 * 8760,
                         "Wind energy produced ({} kWh) does not equal expected value({} kWh)."
                         .format(wind_out['year_one_energy_produced_kwh'], 2 * 8760))
