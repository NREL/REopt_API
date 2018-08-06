import json
import copy
import os
import pandas as pd
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from reo.models import ModelManager
from reo.utilities import check_common_outputs
from reo.validators import ValidateNestedInput
from reo.src.wind import WindSAMSDK


wind_post = {"Scenario": {"Site": {
    "LoadProfile": {
        "annual_kwh": 10000000,
        "doe_reference_name": "MediumOffice"
    },
    "Storage": {
        "max_kwh": 0,
        "max_kw": 0
    },
    "latitude": 39.91065, "longitude": -105.2348,
    "PV": {
        "max_kw": 0
    },
    "Wind": {
        "macrs_bonus_pct": 0.0,
        "max_kw": 10000,
        "federal_itc_pct": 0,
        "macrs_option_years": 0
    },
    "Financial": {
        "om_cost_escalation_pct": 0.001,
        "escalation_pct": 0.006,
        "offtaker_discount_pct": 0.07,
        "analysis_years": 25,
        "offtaker_tax_pct": 0.0
    },
    "ElectricTariff": {
        "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "net_metering_limit_kw": 1e6,
        "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
    }
}}}


class WindTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(WindTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_wind(self):
        """
        Validation run for wind scenario with updated WindToolkit data
        Not validated against REopt desktop, replaces results that matched REopt desktop results as of 9/26/17.
        Note no tax, no ITC, no MACRS.
        :return:
        """

        d_expected = dict()
        d_expected['lcc'] = 9021776
        d_expected['npv'] = 15689004
        d_expected['wind_kw'] = 3734.95
        d_expected['average_annual_energy_exported_wind'] = 5540776
        d_expected['net_capital_costs_plus_om'] = 9008084

        resp = self.get_response(data=wind_post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise

    def test_wind_sam_sdk(self):
        """"
        Validation run for wind data downloaded from Wind Toolkit and run through SAM
        Using wind resource from file directly since WindToolkit data download is spotty
        :return
        """

        resource_data = os.path.join('reo', 'tests', 'wind_data.csv')
        df = pd.read_csv(resource_data, header=0)

        hub_height_meters = 60
        kwargs = dict()
        kwargs['longitude'] = -105.2348
        kwargs['latitude'] = 39.91065
        kwargs['size_class'] = 'medium'

        temperature_kelvin = df["temperature"].tolist()
        temperature_celsius = [x - 273.15 for x in temperature_kelvin]
        kwargs['temperature_celsius'] = temperature_celsius

        pressure_pascals = df["pressure_100m"].tolist()
        pressure_atm = [x / 101325.00 for x in pressure_pascals]
        kwargs['pressure_atmospheres'] = pressure_atm
        kwargs['wind_meters_per_sec'] = df["windspeed"].tolist()
        kwargs['wind_direction_degrees'] = df["winddirection"].tolist()

        sam_wind = WindSAMSDK(hub_height_meters, **kwargs)
        prod_factor = sam_wind.wind_prod_factor()

        prod_factor = [round(x, 3) for x in prod_factor]
        expected_prod_factor = df['prod_factor']
        expected_prod_factor = [round(x, 3) for x in expected_prod_factor]
        self.assertListEqual(prod_factor, expected_prod_factor)

    def test_wind_toolkit_api(self):
        from reo.src.wind_resource import get_wind_resource

        latitude, longitude = 39.7555, -105.2211

        wind_data = get_wind_resource(latitude, longitude, hub_height_meters=40, time_steps_per_hour=4)
        self.assertEqual(len(wind_data['wind_meters_per_sec']), 8760*4)
        wind_data = get_wind_resource(latitude, longitude, hub_height_meters=60, time_steps_per_hour=2)
        self.assertEqual(len(wind_data['wind_meters_per_sec']), 8760 * 2)
        wind_data = get_wind_resource(latitude, longitude, hub_height_meters=80, time_steps_per_hour=1)
        self.assertEqual(len(wind_data['wind_meters_per_sec']), 8760)

    def test_location_outside_wind_toolkit_dataset(self):
        bad_post = copy.deepcopy(wind_post)
        bad_post['Scenario']['Site']['longitude'] = 100
        validator = ValidateNestedInput(bad_post)
        assert(any("Latitude/longitude is outside of wind resource dataset bounds"
                   in e for e in validator.errors['input_errors']))

    def test_validator_fills_in_wind_resource(self):
        validator = ValidateNestedInput(wind_post)
        assert(len(validator.input_dict['Scenario']['Site']['Wind']['wind_meters_per_sec']) == 8760)
