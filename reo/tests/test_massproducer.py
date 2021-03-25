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
import os
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat_chp
from unittest import TestCase, skip  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from reo.models import ModelManager
from reo.utilities import check_common_outputs, MMBTU_TO_KWH

class MassProducerTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(MassProducerTest, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_post = os.path.join('reo', 'tests', 'posts', 'test_massproducer_POST.json')

    def get_response(self, data):

        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_massproducer_nuclear(self):
        """
        This test is specific to a nuclear application with no conventional heating load (LoadProfileBoilerFuel).
        The NewBoiler plus condensing-style SteamTurbine (representing e.g. Nuclear) can produce electricity for meeting the load or 
        mass (e.g. hydrogen) in the MassProducer by feeding it electricity (from the Grid or SteamTurbine) and hot thermal (from NewBoiler).
        Fix the size of the SteamTurbine so that the site imports electricity to supplement the SteamTurbine to produce mass during specific times.
        
        Validation to ensure that:
         1) MassProducer takes electricity from SteamTurbine and/or Grid and hot thermal from NewBoiler to make mass during expected times
         2) 

        :return:
        """

        # Call API, get results in "d" dictionary
        nested_data = json.load(open(self.test_post, 'rb'))

        # Add time of use rates to toggle on/off mass production
        elec_price_high = 0.12  # [$/kWh]
        elec_price_low = 0.12  # [$/kWh]
        wholesale_low = 0.01  # [$/kWh]
        wholesale_high = 0.12  # [$/kWh]
        time_low_start = 8  # timestep index (hour)
        time_low_end = 16  # timestep index (hour)
        mass_value = 8.7  # [$/kg]
        
        pricing_names = ["tou_energy_rates_us_dollars_per_kwh", 
                            "wholesale_rate_us_dollars_per_kwh", 
                            "wholesale_rate_above_site_load_us_dollars_per_kwh"]
        for price in pricing_names:
            if "wholesale" in price:
                price_high = wholesale_high
                price_low = wholesale_low
            else:
                price_high = elec_price_high
                price_low = elec_price_low
            nested_data["Scenario"]["Site"]["ElectricTariff"][
                price] = [price_high] * 8760  # Higher price than value of H2 below ($0.12/kWh)
            nested_data["Scenario"]["Site"]["ElectricTariff"][
                price][time_low_start:time_low_end] = [price_low] * (time_low_end - time_low_start)  # Lower price than H2 value below ($0.12/kWh)
        
        nested_data["Scenario"]["Site"]["MassProducer"][
            "mass_value_us_dollars_per_mass"] = mass_value  # Overwrites value in POST - eqivalent to value of $0.12/kWh electricity

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
     
        # Test expected dispatch from SteamTurbine, NewBoiler, and Grid to the MassProducer and check the consumption of MassProducer
        steamturbine_size_kw = d["outputs"]["Scenario"]["Site"]["SteamTurbine"]["size_kw"]
        steamturbine_electric_to_mp = d["outputs"]["Scenario"]["Site"]["SteamTurbine"]["year_one_electric_to_massproducer_series_kw"] 
        newboiler_thermal_to_mp_mmbtu_per_hr = d["outputs"]["Scenario"]["Site"]["NewBoiler"]["year_one_thermal_to_massproducer_series_mmbtu_per_hr"]
        grid_electric_to_mp = d["outputs"]["Scenario"]["Site"]["ElectricTariff"]["year_one_to_massproducer_series_kw"]
        mp_size_kg_per_hr = d["outputs"]["Scenario"]["Site"]["MassProducer"]["size_mass_per_time"]
        mp_production_kg_per_hr = d["outputs"]["Scenario"]["Site"]["MassProducer"]["year_one_mass_production_series_mass_per_hr"]
        mp_electric_consumed_kwh = d["outputs"]["Scenario"]["Site"]["MassProducer"]["year_one_electric_consumption_kwh"]
        mp_thermal_consumed_mmbtu = d["outputs"]["Scenario"]["Site"]["MassProducer"]["year_one_thermal_consumption_mmbtu"]
        
        # Check that MassProducer produces the maximum amount during the low electricity export price time, and only that time
        expected_mp_production_kg = mp_size_kg_per_hr * (time_low_end - time_low_start)
        self.assertTrue(expected_mp_production_kg, sum(mp_production_kg_per_hr))
        
        # Check that total electric production to MassProducer is equal to total electric consumed by MassProducer
        total_electric_to_mp = sum(steamturbine_electric_to_mp) + sum(grid_electric_to_mp)
        self.assertEqual(mp_electric_consumed_kwh, total_electric_to_mp)

        # Check that total thermal production from NewBoiler to MassProducer is equal to total thermal consumped by MassProducer
        self.assertAlmostEqual(sum(newboiler_thermal_to_mp_mmbtu_per_hr), mp_thermal_consumed_mmbtu, places=3)

