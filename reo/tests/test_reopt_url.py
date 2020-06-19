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
import pickle
from tastypie.test import ResourceTestCaseMixin
from reo.nested_inputs import nested_input_definitions
from reo.validators import ValidateNestedInput
from reo.nested_to_flat_output import nested_to_flat
from django.test import TestCase
from reo.models import ModelManager, ScenarioModel
from reo.utilities import check_common_outputs
from functools import reduce  # forward compatibility for Python 3
import operator
import copy
import logging
logging.disable(logging.CRITICAL)


def get_by_path(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)


def remove_by_path(root, items):
    """Remove a value in a nested object in root by item sequence."""
    del get_by_path(root, items[:-1])[items[-1]]


class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    REopt_tol = 1e-2

    @classmethod
    def setUpClass(cls):
        super(EntryResourceTest, cls).setUpClass()
        cls.data_definitions = nested_input_definitions
        cls.reopt_base = '/v1/job/'
        cls.missing_rate_urdb = pickle.load(open('reo/tests/missing_rate.p','rb'))
        cls.missing_schedule_urdb = pickle.load(open('reo/tests/missing_schedule.p','rb'))
        cls.nested_post = json.load(open('reo/tests/posts/nestedPOST.json'))

    @property
    def complete_valid_nestedpost(self):
        return copy.deepcopy(self.nested_post)

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def check_data_error_response(self, data, text):
        response = self.get_response(data)
        self.assertTrue(text in str(response.content))

    def test_required(self):
        """
        Hit the API with missing required inputs or missing dependencies and verify that the correct message is returned
        """
        required, true_false = self.get_inputs_with_sub_key_from_nested_dict(nested_input_definitions, "required")

        for r in [x for (x,y) in zip(required, true_false) if y is True]:
            test_case = self.complete_valid_nestedpost
            remove_by_path(test_case, r)
            response = self.get_response(test_case)
            text = "Missing Required for {}: {}".format('>'.join(r[:-1]), r[-1])
            err_msg = str(json.loads(response.content)['messages']['input_errors'])
            self.assertTrue(text in err_msg, "'{}' not found in {}".format(text, err_msg))

        electric_tarrif_cases = [['urdb_utility_name', 'urdb_rate_name', 'urdb_response', 'blended_monthly_demand_charges_us_dollars_per_kw'],
                                 ['urdb_utility_name', 'urdb_rate_name', 'urdb_response', 'blended_monthly_rates_us_dollars_per_kwh'],
                                 ['urdb_rate_name',"urdb_response",'blended_monthly_demand_charges_us_dollars_per_kw', 'blended_monthly_rates_us_dollars_per_kwh']]
        for c in electric_tarrif_cases:
            test_case = self.complete_valid_nestedpost
            for r in c:
                del test_case['Scenario']['Site']['ElectricTariff'][r]
            response = self.get_response(test_case)
            text = "Missing Required for Scenario>Site>ElectricTariff"
            self.assertTrue(text in str(json.loads(response.content)['messages']['input_errors']))

        load_profile_cases = [['doe_reference_name', 'annual_kwh', 'monthly_totals_kwh', 'loads_kw'],
                              ['doe_reference_name', 'loads_kw', 'annual_kwh'],
                              ['doe_reference_name', 'loads_kw', 'monthly_totals_kwh']]
        for c in load_profile_cases:
            test_case = self.complete_valid_nestedpost
            for r in c:
                del test_case['Scenario']['Site']['LoadProfile'][r]
            response = self.get_response(test_case)
            text = "Missing Required for Scenario>Site>LoadProfile"
            self.assertTrue(text in str(json.loads(response.content)['messages']['input_errors']))

    def test_valid_data_types(self):

        validator = ValidateNestedInput(self.complete_valid_nestedpost)

        for attribute, test_data in validator.test_data('type'):

            response = self.get_response(test_data)
            text = "Could not convert " + attribute
            err_msg = str(json.loads(response.content)['messages']['input_errors'])
            self.assertTrue(text in err_msg)
            self.assertTrue("(OOPS)" in err_msg)

    def test_outage_hours(self):
        data = self.complete_valid_nestedpost
        data['Scenario']['Site']['LoadProfile']['outage_start_hour'] = 0
        data['Scenario']['Site']['LoadProfile']['outage_end_hour'] = None
        response = self.get_response(data)
        err_msg = str(json.loads(response.content)['messages']['input_errors'])
        self.assertTrue("Missing Required for Scenario>Site>LoadProfile: (outage_end_hour)" in err_msg)

        data['Scenario']['Site']['LoadProfile']['outage_start_hour'] = None
        data['Scenario']['Site']['LoadProfile']['outage_end_hour'] = 0
        response = self.get_response(data)
        err_msg = str(json.loads(response.content)['messages']['input_errors'])
        self.assertTrue("Missing Required for Scenario>Site>LoadProfile: (outage_start_hour)" in err_msg)


        data['Scenario']['Site']['LoadProfile']['outage_start_hour'] = 0
        data['Scenario']['Site']['LoadProfile']['outage_end_hour'] = 0
        response = self.get_response(data)
        err_msg = str(json.loads(response.content)['messages']['input_errors'])
        self.assertTrue("LoadProfile outage_start_hour and outage_end_hour cannot be the same" in err_msg)

    def test_valid_data_ranges(self):

        input = ValidateNestedInput(self.complete_valid_nestedpost)

        for attribute, test_data in input.test_data('min'):
            text = "exceeds allowable min"
            response = self.get_response(test_data)
            err_msg = str(json.loads(response.content)['messages']['input_errors'])
            self.assertTrue(text in err_msg, "'{}' not found in '{}'".format(text, err_msg))

        for attribute, test_data in input.test_data('max'):
            text = "exceeds allowable max"
            response = self.get_response(test_data)
            err_msg = str(json.loads(response.content)['messages']['input_errors'])
            self.assertTrue(text in err_msg, "'{}' not found in '{}'".format(text, err_msg))

        for attribute, test_data in input.test_data('restrict_to'):
            text = "not in allowable inputs"
            response = self.get_response(test_data)
            err_msg = str(json.loads(response.content)['messages']['input_errors'])
            self.assertTrue(text in err_msg, "'{}' not found in '{}'".format(text, err_msg))

    def test_urdb_rate(self):

        data = self.complete_valid_nestedpost

        data['Scenario']['Site']['ElectricTariff']['urdb_response'] = self.missing_rate_urdb
        data['Scenario']['Site']['ElectricTariff']['urdb_response']['label'] = '55fc8115682bea28da645f70'
        text = "URDB Rate (label=55fc8115682bea28da645f70) is currently restricted due to performance limitations"
        self.check_data_error_response(data,text)

        data['Scenario']['Site']['ElectricTariff']['urdb_response'] = self.missing_rate_urdb
        text = "Missing rate/sell/adj attributes for tier 0 in rate 0 energyratestructure"
        self.check_data_error_response(data,text)

        data['Scenario']['Site']['ElectricTariff']['urdb_response'] = self.missing_schedule_urdb

        text = 'energyweekdayschedule contains value 1 which has no associated rate in energyratestructure'
        self.check_data_error_response(data,text)

        text = 'energyweekendschedule contains value 1 which has no associated rate in energyratestructure'
        self.check_data_error_response(data,text)

    def test_complex_incentives(self):
        """
        Tests scenario where: PV has ITC, federal, state, local rebate with maxes, MACRS, bonus, Battery has ITC,
        rebate, MACRS, bonus.
        :return: None
        """
        data = {
        "Scenario": {"webtool_uuid": None, "description": "", "timeout_seconds": 295, "Site": {
            "roof_squarefeet": 5000.0, "longitude": -118.1164613, "address": "", "latitude": 34.5794343,
            "time_steps_per_hour": 1, "user_uuid": None,
            "PV": {"pbi_years": 1.0, "macrs_bonus_pct": 0.4, "max_kw": 1000000000.0, "pbi_max_us_dollars": 1000000000.0, "radius": 0.0, "state_ibi_pct": 0.2, "utility_rebate_max_us_dollars": 10000000000.0, "installed_cost_us_dollars_per_kw": 2000.0, "utility_ibi_max_us_dollars": 10000.0, "tilt": 34.5794343, "federal_rebate_us_dollars_per_kw": 100.0, "gcr": 0.4, "pbi_system_max_kw": 10.0, "utility_ibi_pct": 0.1, "state_ibi_max_us_dollars": 10000.0, "state_rebate_us_dollars_per_kw": 200.0, "macrs_option_years": 5, "state_rebate_max_us_dollars": 10000000000.0, "dc_ac_ratio": 1.1, "federal_itc_pct": 0.3, "pbi_us_dollars_per_kwh": 0.0, "module_type": 1, "array_type": 1, "existing_kw": 0.0, "om_cost_us_dollars_per_kw": 16.0, "utility_rebate_us_dollars_per_kw": 50.0, "min_kw": 0.0, "losses": 0.14, "macrs_itc_reduction": 0.5, "degradation_pct": 0.005, "inv_eff": 0.96, "azimuth": 180.0},
            "Generator": {"pbi_years": 0.0, "macrs_bonus_pct": 0.0, "om_cost_us_dollars_per_kwh": 0.01, "max_kw": 100000000.0, "pbi_max_us_dollars": 0.0, "state_ibi_pct": 0.0, "fuel_intercept_gal_per_hr": 0.0125, "generator_only_runs_during_grid_outage": True, "state_rebate_us_dollars_per_kw": 0.0, "installed_cost_us_dollars_per_kw": 600.0, "utility_ibi_max_us_dollars": 0.0, "fuel_avail_gal": 1000000000.0, "min_turn_down_pct": 0.0, "pbi_system_max_kw": 0.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 0.0, "diesel_fuel_cost_us_dollars_per_gallon": 3.0, "fuel_slope_gal_per_kwh": 0.068, "utility_rebate_max_us_dollars": 0.0, "macrs_option_years": 0, "state_rebate_max_us_dollars": 0.0, "federal_itc_pct": 0.0, "existing_kw": 0.0, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 10.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "macrs_itc_reduction": 0.0, "federal_rebate_us_dollars_per_kw": 0.0, "generator_sells_energy_back_to_grid": False},
            "LoadProfile": {"critical_loads_kw_is_net": False, "critical_load_pct": 0.5, "loads_kw_is_net": True, "loads_kw": [], "outage_end_hour": None, "monthly_totals_kwh": [], "year": 2017, "outage_start_hour": None, "outage_is_major_event": True, "critical_loads_kw": [], "doe_reference_name": "RetailStore", "annual_kwh": 10000000.0},
            "Storage": {"max_kwh": 1000000.0, "rectifier_efficiency_pct": 0.96, "total_itc_pct": 0.0, "min_kw": 0.0, "max_kw": 1000000.0, "replace_cost_us_dollars_per_kw": 460.0, "replace_cost_us_dollars_per_kwh": 230.0, "min_kwh": 0.0, "installed_cost_us_dollars_per_kw": 1000.0, "total_rebate_us_dollars_per_kw": 100, "installed_cost_us_dollars_per_kwh": 500.0, "inverter_efficiency_pct": 0.96, "macrs_itc_reduction": 0.5, "canGridCharge": True, "macrs_bonus_pct": 0.4, "battery_replacement_year": 10, "macrs_option_years": 5, "internal_efficiency_pct": 0.975, "soc_min_pct": 0.2, "soc_init_pct": 0.5, "inverter_replacement_year": 10}, "land_acres": 1.0, "ElectricTariff": {"add_blended_rates_to_urdb_rate": False, "wholesale_rate_us_dollars_per_kwh": 0.0, "net_metering_limit_kw": 0.0, "interconnection_limit_kw": 100000000.0, "urdb_utility_name": "SouthernCaliforniaEdisonCo", "urdb_label": "", "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0, "urdb_rate_name": "TimeofUse,GeneralService,DemandMetered,OptionB:GS-2TOUB,SinglePhase", "urdb_response": {"sector": "Commercial", "peakkwcapacitymax": 200, "utility": "SouthernCaliforniaEdisonCo", "peakkwcapacityhistory": 12, "energyratestructure": [[{"rate": 0.0712, "unit": "kWh"}], [{"rate": 0.09368, "unit": "kWh"}], [{"rate": 0.066, "unit": "kWh"}], [{"rate": 0.08888, "unit": "kWh"}], [{"rate": 0.1355, "unit": "kWh"}]], "energyweekendschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "demandweekendschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "demandrateunit": "kW", "flatdemandstructure": [[{"rate": 13.2}]], "startdate": 1433116800, "phasewiring": "SinglePhase", "eiaid": 17609, "label": "55fc81d7682bea28da64f9ae", "flatdemandunit": "kW", "source": "http://www.sce.com/NR/sc3/tm2/pdf/ce30-12.pdf", "voltagecategory": "Primary", "revisions": [1433408708, 1433409358, 1433516188, 1441198316, 1441199318, 1441199417, 1441199824, 1441199996, 1454521683], "demandweekdayschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "voltageminimum": 2000, "description": "-Energytieredcharge=generationcharge+deliverycharge\\r\\n\\r\\n-Timeofdaydemandcharges(generation-based)aretobeaddedtothemonthlydemandcharge(Deliverybased).", "energyattrs": [{"VoltageDiscount(2KV-<50KV)": "$-0.00106/Kwh"}, {"VoltageDiscount(>50KV<220KV)": "$-0.00238/Kwh"}, {"VoltageDiscountat220KV": "$-0.0024/Kwh"}, {"CaliforniaClimatecredit": "$-0.00669/kwh"}], "energyweekdayschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]], "flatdemandmonths": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "approved": True, "fixedmonthlycharge": 259.2, "enddate": 1451520000, "name": "TimeofUse,GeneralService,DemandMetered,OptionB:GS-2TOUB,SinglePhase", "country": "USA", "uri": "http://en.openei.org/apps/IURDB/rate/view/55fc81d7682bea28da64f9ae", "voltagemaximum": 50000, "peakkwcapacitymin": 20, "demandattrs": [{"FaciltiesVoltageDiscount(2KV-<50KV)": "$-0.18/KW"}, {"FaciltiesVoltageDiscount>50kV-<220kV": "$-5.78/KW"}, {"FaciltiesVoltageDiscount>220kV": "$-9.96/KW"}, {"TimeVoltageDiscount(2KV-<50KV)": "$-0.70/KW"}, {"TimeVoltageDiscount>50kV-<220kV": "$-1.93/KW"}, {"TimeVoltageDiscount>220kV": "$-1.95/KW"}], "demandratestructure": [[{"rate": 0}], [{"rate": 5.3}], [{"rate": 18.11}]]}, "blended_annual_demand_charges_us_dollars_per_kw": 0.0, "blended_annual_rates_us_dollars_per_kwh": 0.0},
            "Financial": {"escalation_pct": 0.026, "offtaker_discount_pct": 0.081, "value_of_lost_load_us_dollars_per_kwh": 100.0, "analysis_years": 20, "microgrid_upgrade_cost_pct": 0.3, "offtaker_tax_pct": 0.4, "om_cost_escalation_pct": 0.025},
            "Wind": {"max_kw": 0.0}
        }}}
        resp = self.get_response(data=data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])

        d_expected = dict()
        d_expected['lcc'] = 10959381
        d_expected['npv'] = 11246374 - d_expected['lcc']
        d_expected['pv_kw'] = 216.667
        d_expected['batt_kw'] = 43.5127
        d_expected['batt_kwh'] = 57.3789
        d_expected['year_one_utility_kwh'] = 9613429.5298

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed.".format(run_uuid))
            print("Error message: {}".format(d['messages'].get('error')))
            raise

    def test_negative_loads(self):
        """
        Ensure that all loads are positive for loads_kw and critical_loads_kw
        :return:
        """

        #Puts -1 for all loads_kw values - leaves criticial_loads_kw blank
        nested_data = {"Scenario": {"webtool_uuid": None, "description": "", "timeout_seconds": 295, "Site": {"PV": {"pbi_years": 1.0, "macrs_bonus_pct": 0.4, "max_kw": 1000000000.0, "pbi_max_us_dollars": 1000000000.0, "radius": 0.0, "state_ibi_pct": 0.0, "utility_rebate_max_us_dollars": 10000000000.0, "installed_cost_us_dollars_per_kw": 2000.0, "utility_ibi_max_us_dollars": 10000000000.0, "tilt": 34.5794343, "federal_rebate_us_dollars_per_kw": 0.0, "gcr": 0.4, "pbi_system_max_kw": 1000000000.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 10000000000.0, "state_rebate_us_dollars_per_kw": 0.0, "macrs_option_years": 5, "state_rebate_max_us_dollars": 10000000000.0, "dc_ac_ratio": 1.1, "federal_itc_pct": 0.3, "pbi_us_dollars_per_kwh": 0.0, "module_type": 1, "array_type": 1, "existing_kw": 0.0, "om_cost_us_dollars_per_kw": 16.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "losses": 0.14, "macrs_itc_reduction": 0.5, "degradation_pct": 0.005, "inv_eff": 0.96, "azimuth": 180.0}, "Generator": {"pbi_years": 0.0, "macrs_bonus_pct": 0.0, "om_cost_us_dollars_per_kwh": 0.01, "max_kw": 0.0, "pbi_max_us_dollars": 0.0, "state_ibi_pct": 0.0, "fuel_intercept_gal_per_hr": 0.0, "generator_only_runs_during_grid_outage": True, "state_rebate_us_dollars_per_kw": 0.0, "installed_cost_us_dollars_per_kw": 600.0, "utility_ibi_max_us_dollars": 0.0, "fuel_avail_gal": 1000000000.0, "min_turn_down_pct": 0.0, "pbi_system_max_kw": 0.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 0.0, "diesel_fuel_cost_us_dollars_per_gallon": 3.0, "fuel_slope_gal_per_kwh": 0.0, "utility_rebate_max_us_dollars": 0.0, "macrs_option_years": 0, "state_rebate_max_us_dollars": 0.0, "federal_itc_pct": 0.0, "existing_kw": 0.0, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 10.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "macrs_itc_reduction": 0.0, "federal_rebate_us_dollars_per_kw": 0.0, "generator_sells_energy_back_to_grid": False}, "LoadProfile": {"critical_loads_kw_is_net": False, "critical_load_pct": 1.0, "loads_kw_is_net": False, "loads_kw": [-1 for _ in range(8760)], "outage_end_hour": None, "monthly_totals_kwh": [], "year": 2017, "outage_start_hour": None, "outage_is_major_event": True, "critical_loads_kw": []}, "roof_squarefeet": 5000.0, "Storage": {"max_kwh": 1000000.0, "rectifier_efficiency_pct": 0.96, "total_itc_pct": 0.0, "min_kw": 0.0, "max_kw": 1000000.0, "replace_cost_us_dollars_per_kw": 460.0, "replace_cost_us_dollars_per_kwh": 230.0, "min_kwh": 0.0, "installed_cost_us_dollars_per_kw": 1000.0, "total_rebate_us_dollars_per_kw": 0, "installed_cost_us_dollars_per_kwh": 500.0, "inverter_efficiency_pct": 0.96, "macrs_itc_reduction": 0.5, "canGridCharge": True, "macrs_bonus_pct": 0.4, "battery_replacement_year": 10, "macrs_option_years": 5, "internal_efficiency_pct": 0.975, "soc_min_pct": 0.2, "soc_init_pct": 0.5, "inverter_replacement_year": 10}, "land_acres": 1.0, "ElectricTariff": {"add_blended_rates_to_urdb_rate": False, "wholesale_rate_us_dollars_per_kwh": 0.0, "net_metering_limit_kw": 0.0, "interconnection_limit_kw": 100000000.0, "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "urdb_utility_name": "Southern California Edison Co", "urdb_label": "", "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0, "urdb_rate_name": "Time of Use, General Service, Demand Metered, Option B: GS-2 TOU B, Single Phase", "urdb_response": {"sector": "Commercial", "peakkwcapacitymax": 200, "utility": "Southern California Edison Co", "peakkwcapacityhistory": 12, "energyratestructure": [[{"rate": 0.0712, "unit": "kWh"}], [{"rate": 0.09368, "unit": "kWh"}], [{"rate": 0.066, "unit": "kWh"}], [{"rate": 0.08888, "unit": "kWh"}], [{"rate": 0.1355, "unit": "kWh"}]], "energyweekendschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "demandweekendschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "demandrateunit": "kW", "flatdemandstructure": [[{"rate": 13.2}]], "startdate": 1433116800, "phasewiring": "Single Phase", "eiaid": 17609, "label": "55fc81d7682bea28da64f9ae", "flatdemandunit": "kW", "source": "http://www.sce.com/NR/sc3/tm2/pdf/ce30-12.pdf", "voltagecategory": "Primary", "revisions": [1433408708, 1433409358, 1433516188, 1441198316, 1441199318, 1441199417, 1441199824, 1441199996, 1454521683], "demandweekdayschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "voltageminimum": 2000, "description": "- Energy tiered charge = generation charge + delivery charge\\r\\n\\r\\n- Time of day demand charges (generation-based) are to be added to the monthly demand charge(Delivery based).", "energyattrs": [{"Voltage Discount (2KV-<50KV)": "$-0.00106/Kwh"}, {"Voltage Discount (>50 KV<220 KV)": "$-0.00238/Kwh"}, {"Voltage Discount at 220 KV": "$-0.0024/Kwh"}, {"California Climate credit": "$-0.00669/kwh"}], "energyweekdayschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]], "flatdemandmonths": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "approved": True, "fixedmonthlycharge": 259.2, "enddate": 1451520000, "name": "Time of Use, General Service, Demand Metered, Option B: GS-2 TOU B, Single Phase", "country": "USA", "uri": "http://en.openei.org/apps/IURDB/rate/view/55fc81d7682bea28da64f9ae", "voltagemaximum": 50000, "peakkwcapacitymin": 20, "demandattrs": [{"Facilties Voltage Discount (2KV-<50KV)": "$-0.18/KW"}, {"Facilties Voltage Discount >50 kV-<220kV": "$-5.78/KW"}, {"Facilties Voltage Discount >220 kV": "$-9.96/KW"}, {"Time Voltage Discount (2KV-<50KV)": "$-0.70/KW"}, {"Time Voltage Discount >50 kV-<220kV": "$-1.93/KW"}, {"Time Voltage Discount >220 kV": "$-1.95/KW"}], "demandratestructure": [[{"rate": 0}], [{"rate": 5.3}], [{"rate": 18.11}]]}, "blended_annual_demand_charges_us_dollars_per_kw": 0.0, "blended_annual_rates_us_dollars_per_kwh": 0.0, "blended_monthly_rates_us_dollars_per_kwh": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}, "longitude": -118.1164613, "address": "", "latitude": 34.5794343, "Financial": {"escalation_pct": 0.026, "offtaker_discount_pct": 0.081, "value_of_lost_load_us_dollars_per_kwh": 100.0, "analysis_years": 20, "microgrid_upgrade_cost_pct": 0.3, "offtaker_tax_pct": 0.4, "om_cost_escalation_pct": 0.025}, "Wind": {"pbi_years": 1.0, "macrs_bonus_pct": 0.0, "max_kw": 0.0, "pbi_max_us_dollars": 1000000000.0, "wind_meters_per_sec": None, "state_ibi_pct": 0.0, "state_rebate_us_dollars_per_kw": 0.0, "installed_cost_us_dollars_per_kw": 3013.0, "utility_ibi_max_us_dollars": 10000000000.0, "pressure_atmospheres": None, "pbi_system_max_kw": 1000000000.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 10000000000.0, "wind_direction_degrees": None, "size_class": "", "utility_rebate_max_us_dollars": 10000000000.0, "macrs_option_years": 5, "state_rebate_max_us_dollars": 10000000000.0, "federal_itc_pct": 0.3, "temperature_celsius": None, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 35.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "macrs_itc_reduction": 0.5, "federal_rebate_us_dollars_per_kw": 0.0}}, "time_steps_per_hour": 1, "user_uuid": None}}
        resp = self.get_response(data=nested_data)
        self.assertIn('loads_kw must contain loads greater than or equal to zero.', str(resp.content))

        #Puts -1 for all critical_loads_kw values and 1 in for all loads_kw

        nested_data = {"Scenario": {"webtool_uuid": None, "description": "", "timeout_seconds": 295, "Site": {"PV": {"pbi_years": 1.0, "macrs_bonus_pct": 0.4, "max_kw": 1000000000.0, "pbi_max_us_dollars": 1000000000.0, "radius": 0.0, "state_ibi_pct": 0.0, "utility_rebate_max_us_dollars": 10000000000.0, "installed_cost_us_dollars_per_kw": 2000.0, "utility_ibi_max_us_dollars": 10000000000.0, "tilt": 34.5794343, "federal_rebate_us_dollars_per_kw": 0.0, "gcr": 0.4, "pbi_system_max_kw": 1000000000.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 10000000000.0, "state_rebate_us_dollars_per_kw": 0.0, "macrs_option_years": 5, "state_rebate_max_us_dollars": 10000000000.0, "dc_ac_ratio": 1.1, "federal_itc_pct": 0.3, "pbi_us_dollars_per_kwh": 0.0, "module_type": 1, "array_type": 1, "existing_kw": 0.0, "om_cost_us_dollars_per_kw": 16.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "losses": 0.14, "macrs_itc_reduction": 0.5, "degradation_pct": 0.005, "inv_eff": 0.96, "azimuth": 180.0}, "Generator": {"pbi_years": 0.0, "macrs_bonus_pct": 0.0, "om_cost_us_dollars_per_kwh": 0.01, "max_kw": 0.0, "pbi_max_us_dollars": 0.0, "state_ibi_pct": 0.0, "fuel_intercept_gal_per_hr": 0.0, "generator_only_runs_during_grid_outage": True, "state_rebate_us_dollars_per_kw": 0.0, "installed_cost_us_dollars_per_kw": 600.0, "utility_ibi_max_us_dollars": 0.0, "fuel_avail_gal": 1000000000.0, "min_turn_down_pct": 0.0, "pbi_system_max_kw": 0.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 0.0, "diesel_fuel_cost_us_dollars_per_gallon": 3.0, "fuel_slope_gal_per_kwh": 0.0, "utility_rebate_max_us_dollars": 0.0, "macrs_option_years": 0, "state_rebate_max_us_dollars": 0.0, "federal_itc_pct": 0.0, "existing_kw": 0.0, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 10.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "macrs_itc_reduction": 0.0, "federal_rebate_us_dollars_per_kw": 0.0, "generator_sells_energy_back_to_grid": False}, "LoadProfile": {"critical_loads_kw_is_net": False, "critical_load_pct": 1.0, "loads_kw_is_net": False, "loads_kw": [1 for _ in range(8760)], "outage_end_hour": None, "monthly_totals_kwh": [], "year": 2017, "outage_start_hour": None, "outage_is_major_event": True, "critical_loads_kw": [-1 for _ in range(8760)]}, "roof_squarefeet": 5000.0, "Storage": {"max_kwh": 1000000.0, "rectifier_efficiency_pct": 0.96, "total_itc_pct": 0.0, "min_kw": 0.0, "max_kw": 1000000.0, "replace_cost_us_dollars_per_kw": 460.0, "replace_cost_us_dollars_per_kwh": 230.0, "min_kwh": 0.0, "installed_cost_us_dollars_per_kw": 1000.0, "total_rebate_us_dollars_per_kw": 0, "installed_cost_us_dollars_per_kwh": 500.0, "inverter_efficiency_pct": 0.96, "macrs_itc_reduction": 0.5, "canGridCharge": True, "macrs_bonus_pct": 0.4, "battery_replacement_year": 10, "macrs_option_years": 5, "internal_efficiency_pct": 0.975, "soc_min_pct": 0.2, "soc_init_pct": 0.5, "inverter_replacement_year": 10}, "land_acres": 1.0, "ElectricTariff": {"add_blended_rates_to_urdb_rate": False, "wholesale_rate_us_dollars_per_kwh": 0.0, "net_metering_limit_kw": 0.0, "interconnection_limit_kw": 100000000.0, "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "urdb_utility_name": "Southern California Edison Co", "urdb_label": "", "wholesale_rate_above_site_load_us_dollars_per_kwh": 0.0, "urdb_rate_name": "Time of Use, General Service, Demand Metered, Option B: GS-2 TOU B, Single Phase", "urdb_response": {"sector": "Commercial", "peakkwcapacitymax": 200, "utility": "Southern California Edison Co", "peakkwcapacityhistory": 12, "energyratestructure": [[{"rate": 0.0712, "unit": "kWh"}], [{"rate": 0.09368, "unit": "kWh"}], [{"rate": 0.066, "unit": "kWh"}], [{"rate": 0.08888, "unit": "kWh"}], [{"rate": 0.1355, "unit": "kWh"}]], "energyweekendschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "demandweekendschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "demandrateunit": "kW", "flatdemandstructure": [[{"rate": 13.2}]], "startdate": 1433116800, "phasewiring": "Single Phase", "eiaid": 17609, "label": "55fc81d7682bea28da64f9ae", "flatdemandunit": "kW", "source": "http://www.sce.com/NR/sc3/tm2/pdf/ce30-12.pdf", "voltagecategory": "Primary", "revisions": [1433408708, 1433409358, 1433516188, 1441198316, 1441199318, 1441199417, 1441199824, 1441199996, 1454521683], "demandweekdayschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "voltageminimum": 2000, "description": "- Energy tiered charge = generation charge + delivery charge\\r\\n\\r\\n- Time of day demand charges (generation-based) are to be added to the monthly demand charge(Delivery based).", "energyattrs": [{"Voltage Discount (2KV-<50KV)": "$-0.00106/Kwh"}, {"Voltage Discount (>50 KV<220 KV)": "$-0.00238/Kwh"}, {"Voltage Discount at 220 KV": "$-0.0024/Kwh"}, {"California Climate credit": "$-0.00669/kwh"}], "energyweekdayschedule": [[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]], "flatdemandmonths": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "approved": True, "fixedmonthlycharge": 259.2, "enddate": 1451520000, "name": "Time of Use, General Service, Demand Metered, Option B: GS-2 TOU B, Single Phase", "country": "USA", "uri": "http://en.openei.org/apps/IURDB/rate/view/55fc81d7682bea28da64f9ae", "voltagemaximum": 50000, "peakkwcapacitymin": 20, "demandattrs": [{"Facilties Voltage Discount (2KV-<50KV)": "$-0.18/KW"}, {"Facilties Voltage Discount >50 kV-<220kV": "$-5.78/KW"}, {"Facilties Voltage Discount >220 kV": "$-9.96/KW"}, {"Time Voltage Discount (2KV-<50KV)": "$-0.70/KW"}, {"Time Voltage Discount >50 kV-<220kV": "$-1.93/KW"}, {"Time Voltage Discount >220 kV": "$-1.95/KW"}], "demandratestructure": [[{"rate": 0}], [{"rate": 5.3}], [{"rate": 18.11}]]}, "blended_annual_demand_charges_us_dollars_per_kw": 0.0, "blended_annual_rates_us_dollars_per_kwh": 0.0, "blended_monthly_rates_us_dollars_per_kwh": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}, "longitude": -118.1164613, "address": "", "latitude": 34.5794343, "Financial": {"escalation_pct": 0.026, "offtaker_discount_pct": 0.081, "value_of_lost_load_us_dollars_per_kwh": 100.0, "analysis_years": 20, "microgrid_upgrade_cost_pct": 0.3, "offtaker_tax_pct": 0.4, "om_cost_escalation_pct": 0.025}, "Wind": {"pbi_years": 1.0, "macrs_bonus_pct": 0.0, "max_kw": 0.0, "pbi_max_us_dollars": 1000000000.0, "wind_meters_per_sec": None, "state_ibi_pct": 0.0, "state_rebate_us_dollars_per_kw": 0.0, "installed_cost_us_dollars_per_kw": 3013.0, "utility_ibi_max_us_dollars": 10000000000.0, "pressure_atmospheres": None, "pbi_system_max_kw": 1000000000.0, "utility_ibi_pct": 0.0, "state_ibi_max_us_dollars": 10000000000.0, "wind_direction_degrees": None, "size_class": "", "utility_rebate_max_us_dollars": 10000000000.0, "macrs_option_years": 5, "state_rebate_max_us_dollars": 10000000000.0, "federal_itc_pct": 0.3, "temperature_celsius": None, "pbi_us_dollars_per_kwh": 0.0, "om_cost_us_dollars_per_kw": 35.0, "utility_rebate_us_dollars_per_kw": 0.0, "min_kw": 0.0, "macrs_itc_reduction": 0.5, "federal_rebate_us_dollars_per_kw": 0.0}}, "time_steps_per_hour": 1, "user_uuid": None}}
        resp = self.get_response(data=nested_data)
        self.assertIn('critical_loads_kw must contain loads greater than or equal to zero.', str(resp.content))

    def test_not_optimal_solution_and_remove_url(self):
        data = {
            "Scenario": {
                "Site": {
                    "latitude": 39.91065, "longitude": -105.2348,
                    "LoadProfile": {
                        "doe_reference_name": "MediumOffice", "annual_kwh": 10000000,
                        "outage_start_hour": 0, "outage_end_hour": 20
                    },
                    "ElectricTariff": {
                        "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2,
                                                                     0.2, 0.2],
                        "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                                                             0.0, 0.0, 0.0, 0.0]
                    },
                    "PV": {
                        "max_kw": 0
                    },
                    "Storage": {
                        "max_kw": 0
                    },
                    "Wind": {
                        "max_kw": 0
                    },
                    "Generator": {
                        "max_kw": 0
                    }
                }
            }
        }
        response = self.get_response(data=data)
        r = json.loads(response.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        self.assertTrue('REopt could not find an optimal solution for these inputs.' in d['messages']['error'])
        # testing "remove" url:
        response = self.api_client.get(self.reopt_base + str(run_uuid) + '/remove')
        self.assertEqual(response.status_code, 204)
        self.assertTrue(len(ScenarioModel.objects.filter(run_uuid=run_uuid)) == 0)

    def get_inputs_with_sub_key_from_nested_dict(self, nested_dict, sub_key, matched_values=None, obj_path=[],
                                                 sub_key_values=[]):
        """
        given a nested dictionary (i.e. nested_inputs_definitions) return all of the keys that contain sub-keys matching
        sub_key
        :param nested_dict:
        :param sub_key:
        :param matched_values: list of str containing desired keys
        :param obj:
        :return:
        """
        if matched_values is None:
            matched_values = []
        for k, v in nested_dict.items():
            if k[0].islower() and isinstance(v, dict):  # then k is an input attribute
                if any(sk == sub_key for sk in nested_dict[k].keys()):
                    matched_values.append(obj_path + [k])
                    sub_key_values.append(nested_dict[k][sub_key])
            elif isinstance(nested_dict[k], dict):  # then k is an abstract input class, dig deeper in nested_dict
                self.get_inputs_with_sub_key_from_nested_dict(nested_dict[k], sub_key, matched_values,
                                                              obj_path=obj_path+[k])
        return matched_values, sub_key_values
