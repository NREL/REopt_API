import json
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
from reo.models import ModelManager


post = {"Scenario": {
    "timeout_seconds": 420,
    "optimality_tolerance_techs": 0.05,
    "Site": {
    "latitude": 37.78, "longitude": -122.45,
    "Financial": {
        "om_cost_escalation_pct": 0.01,
        "escalation_pct": 0.006,
        "offtaker_discount_pct": 0.07,
        "analysis_years": 25,
        "offtaker_tax_pct": 0.0
    },
    "LoadProfile": {
        "doe_reference_name": "Hospital",
    },
    "LoadProfileBoilerFuel": {
        "doe_reference_name": "LargeOffice",
    },
    "LoadProfileChillerThermal": {
        "doe_reference_name": "LargeOffice",
    },    
    "ElectricTariff": {
        "blended_annual_rates_us_dollars_per_kwh": 0.06,
        "blended_annual_demand_charges_us_dollars_per_kw": 0.0
    },
    "FuelTariff": {
        "existing_boiler_fuel_type": "natural_gas",
        "boiler_fuel_blended_monthly_rates_us_dollars_per_mmbtu": [11.0]*12,
        "chp_fuel_type": "natural_gas",
        "chp_fuel_blended_monthly_rates_us_dollars_per_mmbtu": [11.0]*12
    },
    "PV": {
        "max_kw": 0,
    },    
    "Storage": {
        "max_kwh": 0,
        "max_kw": 0
    },
    "ElectricChiller": {
    },
    "Boiler": {
        "boiler_efficiency": 0.8,
        "existing_boiler_production_type_steam_or_hw": "steam",
    }
}}}

class HeatingCoolingTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(HeatingCoolingTest, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):

        return self.api_client.post(self.reopt_base, format='json', data=data)

    #@skip("CHP test")
    def test_heating_cooling_inputs(self):
        
        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        self.assertEqual(round(d['outputs']['Scenario']['Site']['LoadProfileBoilerFuel']['annual_calculated_boiler_fuel_load_mmbtu_bau'],-1), 2900)
        self.assertEqual(round(sum(d['outputs']['Scenario']['Site']['LoadProfileBoilerFuel']['year_one_boiler_fuel_load_series_mmbtu_per_hr']),-1), 2900)
        # The expected cooling load is based on the default **fraction of total electric** profile for the doe_reference_name when annual_tonhour is NOT input
        #    the 320540.0 kWh number is from the default LargeOffice fraction of total electric profile applied to the Hospital default total electric profile
        self.assertEqual(round(d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['annual_calculated_kwh_bau'],-1), 320540.0)
        self.assertEqual(round(sum(d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['year_one_chiller_electric_load_series_kw_bau']),-1), 320540.0)

        post['Scenario']['Site']['LoadProfileBoilerFuel']['doe_reference_name'] = None
        post['Scenario']['Site']['LoadProfileChillerThermal']['doe_reference_name'] = None        
        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        self.assertEqual(round(d['outputs']['Scenario']['Site']['LoadProfileBoilerFuel']['annual_calculated_boiler_fuel_load_mmbtu_bau'],-1), 0)
        self.assertEqual(round(sum(d['outputs']['Scenario']['Site']['LoadProfileBoilerFuel']['year_one_boiler_fuel_load_series_mmbtu_per_hr']),-1),0)
        self.assertEqual(round(d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['annual_calculated_kwh_bau'],-1),0)
        self.assertEqual(round(sum(d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['year_one_chiller_electric_load_series_kw_bau']),-1), 0)

        post['Scenario']['Site']['LoadProfileBoilerFuel']['annual_mmbtu'] = 1000
        post['Scenario']['Site']['LoadProfileChillerThermal']['annual_fraction'] = 0.5
        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        self.assertEqual(round(d['outputs']['Scenario']['Site']['LoadProfileBoilerFuel']['annual_calculated_boiler_fuel_load_mmbtu_bau'],-1), 1000)
        self.assertEqual(round(sum(d['outputs']['Scenario']['Site']['LoadProfileBoilerFuel']['year_one_boiler_fuel_load_series_mmbtu_per_hr']),-1),1000)
        self.assertEqual(round(d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['annual_calculated_kwh_bau'],-1), round(d['outputs']['Scenario']['Site']['LoadProfile']['annual_calculated_kwh'],-1)* 0.5)
        self.assertEqual(round(sum(d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['year_one_chiller_electric_load_series_kw_bau']),-1), 3876410)

        post['Scenario']['Site']['LoadProfileBoilerFuel']['annual_mmbtu'] = None
        post['Scenario']['Site']['LoadProfileChillerThermal']['annual_fraction'] = None
        post['Scenario']['Site']['LoadProfileBoilerFuel']['monthly_mmbtu'] = [1000]*12
        post['Scenario']['Site']['LoadProfileChillerThermal']['monthly_fraction'] = [0.1] * 12
        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        self.assertEqual(round(d['outputs']['Scenario']['Site']['LoadProfileBoilerFuel']['annual_calculated_boiler_fuel_load_mmbtu_bau'],-1), 12000)
        self.assertEqual(round(sum(d['outputs']['Scenario']['Site']['LoadProfileBoilerFuel']['year_one_boiler_fuel_load_series_mmbtu_per_hr']),-1), 12000)
        self.assertEqual(round(d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['annual_calculated_kwh_bau'] - (d['outputs']['Scenario']['Site']['LoadProfile']['annual_calculated_kwh']* 0.1),-1),0)
        self.assertEqual(round(sum(d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['year_one_chiller_electric_load_series_kw_bau']),-1), 775280)

        post['Scenario']['Site']['LoadProfileBoilerFuel']['annual_calculated_boiler_fuel_load_mmbtu_bau'] = None
        post['Scenario']['Site']['LoadProfileChillerThermal']['annual_fraction'] = None
        post['Scenario']['Site']['LoadProfileBoilerFuel']['monthly_totals_kwh'] = None
        post['Scenario']['Site']['LoadProfileChillerThermal']['monthly_fraction'] = None
        post['Scenario']['Site']['LoadProfileBoilerFuel']['loads_mmbtu_per_hour'] = [1]*8760
        post['Scenario']['Site']['LoadProfileChillerThermal']['loads_fraction'] = [0.01]*8760
        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        self.assertEqual(round(d['outputs']['Scenario']['Site']['LoadProfileBoilerFuel']['annual_calculated_boiler_fuel_load_mmbtu_bau'],-1), 8760)
        self.assertEqual(round(sum(d['outputs']['Scenario']['Site']['LoadProfileBoilerFuel']['year_one_boiler_fuel_load_series_mmbtu_per_hr']),-1),8760)
        self.assertEqual(round(d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['annual_calculated_kwh_bau'] - (d['outputs']['Scenario']['Site']['LoadProfile']['annual_calculated_kwh']* 0.01),-1),0)
        self.assertEqual(round(sum(d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['year_one_chiller_electric_load_series_kw_bau']),-1), 77530.0)