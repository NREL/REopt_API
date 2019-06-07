import json
import copy
import os
import pandas as pd
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from unittest import skip
from reo.models import ModelManager
from reo.utilities import check_common_outputs
from reo.validators import ValidateNestedInput
from reo.src.wind import WindSAMSDK, combine_wind_files


wind_post = {"Scenario": {"Site": {
    "LoadProfile": {
        "annual_kwh": 100000,
        "doe_reference_name": "MidriseApartment"
    },
    "Storage": {
        "max_kwh": 0,
        "max_kw": 0
    },
    "latitude": 39.91065, "longitude": -105.2348,
    "PV": {
        "max_kw": 0
    },
    "Generator": {
        "max_kw": 0
    },
    "Wind": {
        "macrs_bonus_pct": 0.0,
        "max_kw": 10,
        "federal_itc_pct": 0,
        "macrs_option_years": 0,
        "size_class": 'commercial',
        "installed_cost_us_dollars_per_kw": 4555

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


    def test_wind_size_class(self):
        """
        Validation to ensure that max_kw of wind is set to size_class
        Annual kWh results in roughly 11 kW average load, going into commercial size_class for wind (max_kw = 100)
        Trying to set min_kw to 1000 should result in min_kw getting reset to max_kw for size_class and wind_kw coming to 100 kW
        :return:
        """

        wind_post_updated = wind_post
        wind_post_updated["Scenario"]["Site"]["LoadProfile"]["annual_kwh"] = 100000
        wind_post_updated["Scenario"]["Site"]["Wind"]["min_kw"] = 0

        # For some reason, when running full suite, validators isn't run, and this is not updated
        wind_post_updated["Scenario"]["Site"]["Wind"]["size_class"] = "commercial"


        d_expected = dict()
        d_expected['wind_kw'] = 100


        resp = self.get_response(data=wind_post_updated)
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

    def test_wind(self):
        """
        Validation run for wind scenario with updated WindToolkit data
        Not validated against REopt desktop, replaces results that matched REopt desktop results as of 9/26/17.
        Note no tax, no ITC, no MACRS.
        :return:
        """

        d_expected = dict()
        d_expected['lcc'] = 8551172
        d_expected['npv'] = 16159608
        d_expected['wind_kw'] = 3734.95
        d_expected['average_annual_energy_exported_wind'] = 5540765
        d_expected['net_capital_costs_plus_om'] = 8537480

        resp = self.get_response(data=wind_post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])
        print(c.keys())

        """
        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise
        """

    def test_wind_sam_sdk(self):
        """"
        Validation run for wind data downloaded from Wind Toolkit and run through SAM
        Using wind resource from file directly since WindToolkit data download is spotty
        :return
        """

        # First test passing in data in memory directly
        path_inputs = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wind_resource')
        resource_data = os.path.join(path_inputs, 'wind_data.csv')
        df = pd.read_csv(resource_data, header=0)

        # By default, the weather data available for download as a .srw file through WindTookit website only gives 100 m
        # hub height, which is what was used for SAM comparison. SAM won't let you simulate a hub height that differs
        # from the resource by more than 35m, so we'll use 80m for validation
        kwargs = dict()
        kwargs['hub_height_meters'] = 80
        kwargs['longitude'] = -105.2348
        kwargs['latitude'] = 39.91065
        kwargs['size_class'] = 'medium'
        kwargs['path_inputs'] = path_inputs
        kwargs['temperature_celsius'] = df["temperature"].tolist()
        kwargs['pressure_atmospheres'] = df["pressure_100m"].tolist()
        kwargs['wind_meters_per_sec'] = df["windspeed"].tolist()
        kwargs['wind_direction_degrees'] = df["winddirection"].tolist()

        sam_wind = WindSAMSDK(**kwargs)
        prod_factor = sam_wind.wind_prod_factor()

        prod_factor = [round(x, 2) for x in prod_factor]
        expected_prod_factor = df['prod_factor']
        expected_prod_factor = [round(x, 2) for x in expected_prod_factor]
        self.assertListEqual(prod_factor, expected_prod_factor)

        # Second test passing in resource file
        kwargs2 = dict()
        kwargs2['hub_height_meters'] = 50
        kwargs['longitude'] = -105.2348
        kwargs['latitude'] = 39.91065
        kwargs['size_class'] = 'medium'
        kwargs2['file_resource_full'] = os.path.join(path_inputs, "39.91065_-105.2348_windtoolkit_2012_60min_40m_60m.srw")

        sam_wind2 = WindSAMSDK(**kwargs2)
        prod_factor2 = sam_wind2.wind_prod_factor()
        self.assertEqual(len(prod_factor2), 8760)

    def test_combine_wind(self):

        path_inputs = os.path.join('reo', 'tests', 'wind_resource')

        file1 = os.path.join(path_inputs, "39.91065_-105.2348_windtoolkit_2012_60min_40m.srw")
        file2 = os.path.join(path_inputs, "39.91065_-105.2348_windtoolkit_2012_60min_60m.srw")
        file_out = os.path.join(path_inputs, "39.91065_-105.2348_windtoolkit_2012_60min_40m_60m.srw")

        file_resource_heights = {40: file1, 60: file2}

        if os.path.isfile(file_out):
            os.remove(file_out)
        self.assertTrue(combine_wind_files(file_resource_heights, file_out))

    @skip("HSDS wind api barely works")
    def test_wind_hsds_api(self):
        from reo.src.wind_resource import get_wind_resource_hsds

        latitude, longitude = 39.7555, -105.2211

        wind_data = get_wind_resource_hsds(latitude, longitude, hub_height_meters=40, time_steps_per_hour=4)
        self.assertEqual(len(wind_data['wind_meters_per_sec']), 8760*4)
        wind_data = get_wind_resource_hsds(latitude, longitude, hub_height_meters=80, time_steps_per_hour=1)
        self.assertEqual(len(wind_data['wind_meters_per_sec']), 8760)

    def test_location_outside_wind_toolkit_dataset(self):
        bad_post = copy.deepcopy(wind_post)
        bad_post['Scenario']['Site']['longitude'] = 100
        validator = ValidateNestedInput(bad_post)
        assert(any("Latitude/Longitude is outside of wind resource dataset bounds"
                   in e for e in validator.errors['input_errors']))
