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
import pandas as pd
import numpy as np
from unittest import skip


class ColdTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(ColdTest, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_post = os.path.join('reo', 'tests', 'posts', 'test_cold_POST.json')

    def get_response(self, data):

        return self.api_client.post(self.reopt_base, format='json', data=data)

    @skip("CHP test")
    def test_heat_cool_energy_balance(self):
        """

        This is an "energy balance" type of test which tests the model formulation/math as opposed
            to a specific scenario. This test is robust to changes in the model "MIPRELSTOP" or "MAXTIME" setting

        Validation to ensure that:
         1) The electric chiller and absorption chiller are supplying 100% of the cooling thermal load
         2) The boiler is supplying the boiler heating load plus additional absorption chiller thermal load
         3) The Cold and Hot TES efficiency (charge loss and thermal decay) are being tracked properly

        :return:
        """

        # Original non cooling and cooling electric loads, and conversion to cooling thermal load
        total_electric_load_total = 7752810.3175
        cooling_electric_load_total = 1427328.0614
        cooling_thermal_load_ton_hr_total = cooling_electric_load_total * 3.4 / 3.51685

        # Original boiler fuel and thermal loads
        boiler_fuel_consumption_expected = 12241.814
        boiler_thermal_mmbtu_expected = boiler_fuel_consumption_expected * 0.78

        # Call API, get results in "d" dictionary
        nested_data = json.load(open(self.test_post, 'rb'))
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        # Cooling outputs
        cooling_elecchl_electric_consumption_calculated = d['outputs']['Scenario']['Site']['ElectricChiller']['year_one_electric_chiller_electric_consumption_kwh']
        cooling_elecchl_tons_to_load_series = d['outputs']['Scenario']['Site']['ElectricChiller']['year_one_electric_chiller_thermal_to_load_series_ton']
        cooling_elecchl_tons_to_tes_series = d['outputs']['Scenario']['Site']['ElectricChiller']['year_one_electric_chiller_thermal_to_tes_series_ton']
        cooling_absorpchl_tons_to_load_series = d['outputs']['Scenario']['Site']['AbsorptionChiller']['year_one_absorp_chl_thermal_to_load_series_ton']
        cooling_absorpchl_tons_to_tes_series = d['outputs']['Scenario']['Site']['AbsorptionChiller']['year_one_absorp_chl_thermal_to_tes_series_ton']
        cooling_ton_hr_to_load_tech_total = sum(cooling_elecchl_tons_to_load_series) + sum(cooling_absorpchl_tons_to_load_series)
        cooling_ton_hr_to_tes_total = sum(cooling_elecchl_tons_to_tes_series) + sum(cooling_absorpchl_tons_to_tes_series)
        cooling_tes_tons_to_load_series = d['outputs']['Scenario']['Site']['ColdTES']['year_one_thermal_from_cold_tes_series_ton'] or []
        cooling_ton_hr_to_load_total = cooling_ton_hr_to_load_tech_total + sum(cooling_tes_tons_to_load_series)
        cooling_extra_from_tes_losses = cooling_ton_hr_to_tes_total - sum(cooling_tes_tons_to_load_series)
        tes_effic_with_decay = sum(cooling_tes_tons_to_load_series) / cooling_ton_hr_to_tes_total
        cooling_total_prod_from_techs = cooling_ton_hr_to_load_tech_total + cooling_ton_hr_to_tes_total
        cooling_load_plus_tes_losses = cooling_thermal_load_ton_hr_total + cooling_extra_from_tes_losses

        # Check if sum of electric and absorption chillers equals cooling thermal total
        #self.assertAlmostEqual(cooling_elecchl_electric_consumption_calculated, cooling_electric_load_total, delta=5.0)
        self.assertGreater(0.97, tes_effic_with_decay)
        self.assertAlmostEqual(cooling_total_prod_from_techs, cooling_load_plus_tes_losses, delta=5.0)

        # Heating outputs
        boiler_fuel_consumption_calculated = d['outputs']['Scenario']['Site']['Boiler']['year_one_boiler_fuel_consumption_mmbtu']
        boiler_thermal_series = d['outputs']['Scenario']['Site']['Boiler']['year_one_boiler_thermal_production_series_mmbtu_per_hr']
        boiler_thermal_to_load_series = d['outputs']['Scenario']['Site']['Boiler']['year_one_thermal_to_load_series_mmbtu_per_hour']
        boiler_thermal_to_tes_series = d['outputs']['Scenario']['Site']['Boiler']['year_one_thermal_to_tes_series_mmbtu_per_hour']
        chp_thermal_to_load_series = d['outputs']['Scenario']['Site']['CHP']['year_one_thermal_to_load_series_mmbtu_per_hour']
        chp_thermal_to_tes_series = d['outputs']['Scenario']['Site']['CHP']['year_one_thermal_to_tes_series_mmbtu_per_hour']
        chp_thermal_to_waste_series = d['outputs']['Scenario']['Site']['CHP']['year_one_thermal_to_waste_series_mmbtu_per_hour']
        absorpchl_thermal_series = d['outputs']['Scenario']['Site']['AbsorptionChiller']['year_one_absorp_chl_thermal_consumption_series_mmbtu_per_hr']
        hot_tes_mmbtu_per_hr_to_load_series = d['outputs']['Scenario']['Site']['HotTES']['year_one_thermal_from_hot_tes_series_mmbtu_per_hr']
        tes_inflows = sum(chp_thermal_to_tes_series) + sum(boiler_thermal_to_tes_series)
        total_chp_production = sum(chp_thermal_to_load_series) + sum(chp_thermal_to_tes_series) + sum(chp_thermal_to_waste_series)
        tes_outflows = sum(hot_tes_mmbtu_per_hr_to_load_series)
        new_total_thermal_expected = boiler_thermal_mmbtu_expected + sum(absorpchl_thermal_series) + sum(chp_thermal_to_waste_series) + tes_inflows
        new_boiler_fuel_expected = (new_total_thermal_expected - total_chp_production - tes_outflows) / 0.78
        total_thermal_mmbtu_calculated = sum(boiler_thermal_series) + total_chp_production + tes_outflows

        self.assertAlmostEqual(boiler_fuel_consumption_calculated, new_boiler_fuel_expected, delta=8.0)
        self.assertAlmostEqual(total_thermal_mmbtu_calculated, new_total_thermal_expected, delta=8.0)



