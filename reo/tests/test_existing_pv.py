import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class TestExistingPV(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestExistingPV, self).setUp()

        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = {"Scenario": {"webtool_uuid": None, "description": "", "timeout_seconds": 295, 
        "Site": {
          "PV": {"pbi_years": 1.0, "macrs_bonus_pct": 0.0, "max_kw": 100.0, "pbi_max_us_dollars": 1000000000.0, "radius": 0.0, "state_ibi_pct": 0.0, "state_rebate_us_dollars_per_kw": 0.0, "installed_cost_us_dollars_per_kw": 2000.0, "utility_ibi_max_us_dollars": 10000000000.0, "tilt": 35.2468, "degradation_pct": 0.005, "gcr": 0.4, "pbi_system_max_kw": 1000000000.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 10000000000.0, "utility_rebate_max_us_dollars": 10000000000.0, "macrs_option_years": 5, "state_rebate_max_us_dollars": 10000000000.0, "dc_ac_ratio": 1.1, "federal_itc_pct": 0.3, "existing_kw": 0.0, "module_type": 0, "array_type": 0, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 16.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "losses": 0.14, "macrs_itc_reduction": 0.5, "federal_rebate_us_dollars_per_kw": 0.0, "inv_eff": 0.96, "azimuth": 180.0}, 
          "Generator": {"pbi_years": 0.0, "macrs_bonus_pct": 0.0, "om_cost_us_dollars_per_kwh": 0.01, "max_kw": 1000000000.0, "pbi_max_us_dollars": 0.0, "state_ibi_pct": 0.0, "fuel_intercept_gal_per_hr": 0.0125, "generator_only_runs_during_grid_outage": True, "utility_rebate_max_us_dollars": 0.0, "installed_cost_us_dollars_per_kw": 600.0, "utility_ibi_max_us_dollars": 0.0, "fuel_avail_gal": 1000000000.0, "min_turn_down_pct": 0.0, "pbi_system_max_kw": 0.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 0.0, "diesel_fuel_cost_us_dollars_per_gallon": 3.0, "fuel_slope_gal_per_kwh": 0.068, "state_rebate_us_dollars_per_kw": 0.0, "macrs_option_years": 0, "state_rebate_max_us_dollars": 0.0, "federal_itc_pct": 0.0, "pbi_us_dollars_per_kwh": 0.0, "existing_kw": 0.0, "om_cost_us_dollars_per_kw": 10.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "macrs_itc_reduction": 0.0, "federal_rebate_us_dollars_per_kw": 0.0, "generator_sells_energy_back_to_grid": False}, 
          "LoadProfile": {"critical_loads_kw_is_net": False, "year": 2017, "loads_kw_is_net": True, "outage_start_hour": None, "outage_end_hour": None, "monthly_totals_kwh": [], "critical_load_pct": 0.5, "outage_is_major_event": True, "critical_loads_kw": [], "doe_reference_name": "MidriseApartment", "annual_kwh": None}, 
          "address": "", 
          "Storage": {"max_kwh": 0.0, "rectifier_efficiency_pct": 0.96, "total_itc_pct": 0.0, "min_kw": 0.0, "max_kw": 0.0, "replace_cost_us_dollars_per_kw": 460.0, "replace_cost_us_dollars_per_kwh": 230.0, "min_kwh": 0.0, "installed_cost_us_dollars_per_kw": 1000.0, "total_rebate_us_dollars_per_kw": 0, "installed_cost_us_dollars_per_kwh": 500.0, "inverter_efficiency_pct": 0.96, "battery_replacement_year": 10, "canGridCharge": True, "macrs_bonus_pct": 0.0, "macrs_itc_reduction": 0.5, "macrs_option_years": 7, "internal_efficiency_pct": 0.975, "soc_min_pct": 0.2, "soc_init_pct": 0.5, "inverter_replacement_year": 10}, 
          "land_acres": None, 
          "ElectricTariff": {"add_blended_rates_to_urdb_rate": False, "wholesale_rate_us_dollars_per_kwh": 0.0, "net_metering_limit_kw": 0.0, "interconnection_limit_kw": 100000000.0, "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "urdb_utility_name": "", "urdb_label": "", "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0, "urdb_rate_name": "", "urdb_response": None, "blended_annual_demand_charges_us_dollars_per_kw": 0.0, "blended_annual_rates_us_dollars_per_kwh": 0.0, "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]}, 
          "longitude": -91.7337, 
          "roof_squarefeet": None, 
          "latitude": 35.2468, 
          "Financial": {"escalation_pct": 0.026, "offtaker_discount_pct": 0.081, "value_of_lost_load_us_dollars_per_kwh": 100.0, "analysis_years": 20, "microgrid_upgrade_cost_pct": 0.3, "offtaker_tax_pct": 0.26, "om_cost_escalation_pct": 0.025}, "Wind": {"pbi_years": 1.0, "macrs_bonus_pct": 0.0, "max_kw": 0.0, "pbi_max_us_dollars": 1000000000.0, "wind_meters_per_sec": None, "state_ibi_pct": 0.0, "utility_rebate_max_us_dollars": 10000000000.0, "installed_cost_us_dollars_per_kw": 3013.0, "utility_ibi_max_us_dollars": 10000000000.0, "pressure_atmospheres": None, "pbi_system_max_kw": 1000000000.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 10000000000.0, "wind_direction_degrees": None, "size_class": "", "state_rebate_us_dollars_per_kw": 0.0, "macrs_option_years": 5, "state_rebate_max_us_dollars": 10000000000.0, "federal_itc_pct": 0.3, "temperature_celsius": None, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 35.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "macrs_itc_reduction": 0.5, "federal_rebate_us_dollars_per_kw": 0.0}}, 
          "time_steps_per_hour": 1, "user_uuid": None}}

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

    def test_existing_pv(self):
        """
        Pass in existing PV size = PV max_kw and verify that:
        - sized system is existing_kw
        - zero capital costs (battery size set to zero)
        - npv is zero (i.e. same benefits in BAU with existing PV as in cost-optimal scenario.)

        Also pass in PV array type as 0 (ground mount fixed) and verify that:
        - the default tilt angle gets set equal to the latitude (given that 'tilt' is not provided as input)
        ...
        - production incentives applied to existing PV
        """

        class ClassAttributes:
            def __init__(self, dictionary):
                for k, v in dictionary.items():
                    setattr(self, k, v)

        pv_size = 100
        existing_kw = pv_size
        max_kw = pv_size
        flat_load = [pv_size] * 8760

        self.post['Scenario']['Site']['PV']['existing_kw'] = existing_kw
        self.post['Scenario']['Site']['PV']['max_kw'] = 0
        self.post['Scenario']['Site']['PV']['array_type'] = 0
        self.post['Scenario']['Site']['LoadProfile']['loads_kw_is_net'] = True
        self.post['Scenario']['Site']['LoadProfile']['loads_kw'] = flat_load

        response = self.get_response(self.post)        
        pv_out = ClassAttributes(response['outputs']['Scenario']['Site']['PV'])
        load_out = ClassAttributes(response['outputs']['Scenario']['Site']['LoadProfile'])
        financial = ClassAttributes(response['outputs']['Scenario']['Site']['Financial'])
        latitude_input = response['inputs']['Scenario']['Site']['latitude']
        tilt_out = response['inputs']['Scenario']['Site']['PV']['tilt']
        messages = ClassAttributes(response['messages'])
        net_load = [a - round(b,3) for a, b in zip(load_out.year_one_electric_load_series_kw, pv_out.year_one_power_production_series_kw)]
        try:
            self.assertEqual(existing_kw, pv_out.size_kw,
                             "Existing PV size ({} kW) does not equal REopt PV size ({} kW)."
                             .format(pv_size, pv_out.size_kw))

            self.assertEqual(financial.net_capital_costs, 0,
                             "Non-zero capital cost for existing PV: {}."
                             .format(financial.net_capital_costs))

            self.assertEqual(financial.npv_us_dollars, 0,
                             "Non-zero NPV with existing PV in both BAU and cost-optimal scenarios: {}."
                             .format(financial.npv_us_dollars))

            self.assertEqual(tilt_out, latitude_input,
                             "Tilt default should be equal latitude for ground-mount fixed array_type input")

            # self.assertListEqual(flat_load, net_load)  # takes forever!
            zero_list = [round(a - b, 2) for a, b in zip(flat_load, net_load)]
            zero_sum = sum(zero_list)
            self.assertEqual(zero_sum, 0, "Net load is not being calculated correctly.")

        except Exception as e:
            error_msg = None
            if hasattr(messages, "error"):
                error_msg = messages.error
            print("test_existing_pv API error message: {}".format(error_msg))
            print("Run uuid: {}".format(response['outputs']['Scenario']['run_uuid']))
            raise e
