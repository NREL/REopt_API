# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
import json
import copy
import os
import pandas as pd
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat
from django.test import TestCase  
from reo.models import ModelManager
from reo.utilities import check_common_outputs
from reo.validators import ValidateNestedInput
from reo.src.wind import WindSAMSDK, combine_wind_files
import logging
logging.disable(logging.CRITICAL)


wind_post = {"Scenario":
                 {"webtool_uuid": None,
                  "description": "",
                  "timeout_seconds": 295,
                  "Site": {
                      "PV": {"pbi_years": 1.0, "macrs_bonus_pct": 0.0, "max_kw": 0.0, "pbi_max_us_dollars": 1000000000.0, "radius": 0.0, "state_ibi_pct": 0.0, "utility_rebate_max_us_dollars": 10000000000.0, "installed_cost_us_dollars_per_kw": 2000.0, "utility_ibi_max_us_dollars": 10000000000.0, "tilt": 0.537, "federal_rebate_us_dollars_per_kw": 0.0, "gcr": 0.4, "pbi_system_max_kw": 1000000000.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 10000000000.0, "state_rebate_us_dollars_per_kw": 0.0, "macrs_option_years": 5, "state_rebate_max_us_dollars": 10000000000.0, "dc_ac_ratio": 1.1, "federal_itc_pct": 0.3, "pbi_us_dollars_per_kwh": 0.0, "module_type": 0, "array_type": 1, "existing_kw": 0.0, "om_cost_us_dollars_per_kw": 16.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "losses": 0.14, "macrs_itc_reduction": 0.5, "degradation_pct": 0.005, "inv_eff": 0.96, "azimuth": 180.0},
                      "Generator": {"pbi_years": 0.0, "macrs_bonus_pct": 0.0, "om_cost_us_dollars_per_kwh": 0.01, "max_kw": 0.0, "pbi_max_us_dollars": 0.0, "state_ibi_pct": 0.0, "fuel_intercept_gal_per_hr": 0.0, "generator_only_runs_during_grid_outage": True, "state_rebate_us_dollars_per_kw": 0.0, "installed_cost_us_dollars_per_kw": 600.0, "utility_ibi_max_us_dollars": 0.0, "fuel_avail_gal": 1000000000.0, "min_turn_down_pct": 0.0, "pbi_system_max_kw": 0.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 0.0, "diesel_fuel_cost_us_dollars_per_gallon": 3.0, "fuel_slope_gal_per_kwh": 0.0, "utility_rebate_max_us_dollars": 0.0, "macrs_option_years": 0, "state_rebate_max_us_dollars": 0.0, "federal_itc_pct": 0.0, "existing_kw": 0.0, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 10.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "macrs_itc_reduction": 0.0, "federal_rebate_us_dollars_per_kw": 0.0, "generator_sells_energy_back_to_grid": False},
                      "LoadProfile": {"critical_loads_kw_is_net": False, "critical_load_pct": 0.5, "loads_kw_is_net": True, "loads_kw": [], "outage_end_time_step": None, "monthly_totals_kwh": [], "year": 2017, "outage_start_time_step": None, "outage_is_major_event": True, "critical_loads_kw": [], "doe_reference_name": "MidriseApartment", "annual_kwh": 100000.0},
                      "roof_squarefeet": None,
                      "Storage": {"max_kwh": 0.0, "rectifier_efficiency_pct": 0.96, "total_itc_pct": 0.0, "min_kw": 0.0, "max_kw": 0.0, "replace_cost_us_dollars_per_kw": 460.0, "replace_cost_us_dollars_per_kwh": 230.0, "min_kwh": 0.0, "installed_cost_us_dollars_per_kw": 1000.0, "total_rebate_us_dollars_per_kw": 0, "installed_cost_us_dollars_per_kwh": 500.0, "inverter_efficiency_pct": 0.96, "macrs_itc_reduction": 0.5, "canGridCharge": True, "macrs_bonus_pct": 0.0, "battery_replacement_year": 10, "macrs_option_years": 7, "internal_efficiency_pct": 0.975, "soc_min_pct": 0.2, "soc_init_pct": 0.5, "inverter_replacement_year": 10},
                      "land_acres": None,
                      "ElectricTariff": {"add_blended_rates_to_urdb_rate": False, "wholesale_rate_us_dollars_per_kwh": 0.0, "net_metering_limit_kw": 1000000.0, "interconnection_limit_kw": 100000000.0, "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "urdb_utility_name": "", "urdb_label": "", "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0, "urdb_rate_name": "", "urdb_response": None, "blended_annual_demand_charges_us_dollars_per_kw": 0.0, "blended_annual_rates_us_dollars_per_kwh": 0.0, "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]},
                      "longitude": -105.2348, "address": "",
                      "latitude": 39.91065,
                      "Financial": {"escalation_pct": 0.006, "offtaker_discount_pct": 0.07, "value_of_lost_load_us_dollars_per_kwh": 100.0, "analysis_years": 25, "microgrid_upgrade_cost_pct": 0.3, "offtaker_tax_pct": 0.0, "om_cost_escalation_pct": 0.001},
                      "Wind": {"pbi_years": 1.0, "macrs_bonus_pct": 0.0, "max_kw": 10.0, "pbi_max_us_dollars": 1000000000.0, "wind_meters_per_sec": None, "state_ibi_pct": 0.0, "state_rebate_us_dollars_per_kw": 0.0, "installed_cost_us_dollars_per_kw": 4555.0, "utility_ibi_max_us_dollars": 10000000000.0, "pressure_atmospheres": None, "pbi_system_max_kw": 1000000000.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 10000000000.0, "wind_direction_degrees": None, "size_class": "commercial", "utility_rebate_max_us_dollars": 10000000000.0, "macrs_option_years": 0, "state_rebate_max_us_dollars": 10000000000.0, "federal_itc_pct": 0.0, "temperature_celsius": None, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 35.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "macrs_itc_reduction": 0.5, "federal_rebate_us_dollars_per_kw": 0.0}
                  },
                  "time_steps_per_hour": 1, "user_uuid": None}
             }


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
        Note no tax, no ITC, no MACRS.
        :return:
        """
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
                "installed_cost_us_dollars_per_kw": 1874,
                "om_cost_us_dollars_per_kw": 35,
                "macrs_bonus_pct": 0.0,
                "max_kw": 10000,
                "federal_itc_pct": 0,
                "macrs_option_years": 0,
                "size_class": "large"
            },
            "Financial": {
                "om_cost_escalation_pct": 0.001,
                "escalation_pct": 0.006,
                "offtaker_discount_pct": 0.07,
                "analysis_years": 25,
                "offtaker_tax_pct": 0.0
            },
            "ElectricTariff": {
                "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                                                     0.0, 0.0],
                "net_metering_limit_kw": 1e6,
                "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
            }
        }}}
        d_expected = dict()
        d_expected['lcc'] = 8551172
        d_expected['npv'] = 16159608
        d_expected['wind_kw'] = 3735
        d_expected['average_annual_energy_exported_wind'] = 5844282
        d_expected['net_capital_costs_plus_om'] = 8537480
        resp = self.get_response(data=wind_post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        err_messages = d['messages'].get('error') or []
        if 'Wind Dataset Timed Out' in err_messages:
            print("Wind Dataset Timed Out")
        else:
            c = nested_to_flat(d['outputs'])
            try:
                check_common_outputs(self, c, d_expected)
            except:
                print("Run {} expected outputs may have changed.".format(run_uuid))
                print("Error message: {}".format(d['messages'].get('error')))
                raise

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

    def test_location_outside_wind_toolkit_dataset(self):
        bad_post = copy.deepcopy(wind_post)
        bad_post['Scenario']['Site']['longitude'] = 100
        validator = ValidateNestedInput(bad_post)
        assert(any("Latitude/Longitude is outside of wind resource dataset bounds"
                   in e for e in validator.errors['input_errors']))
