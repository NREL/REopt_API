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
from django.test import TestCase
from reo.models import ModelManager
from reo.utilities import MMBTU_TO_KWH

class NewBoilerSteamTurbineTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(NewBoilerSteamTurbineTest, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_post = os.path.join('reo', 'tests', 'posts', 'test_newboiler_st_POST.json')

    def get_response(self, data):

        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_newboiler_steamturbine(self):
        """
        Validation to ensure that:
         1) NewBoiler can serve the heating load or provide condensing-style SteamTurbine with steam to produce power
         2) SteamTurbine serves the electric loads/storage
         3) SteamTurbine can export energy to the grid

        :return:
        """

        # Call API, get results in "d" dictionary
        nested_data = json.load(open(self.test_post, 'rb'))

        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
     
        # BAU boiler loads
        load_boiler_fuel = d["outputs"]["Scenario"]["Site"]["LoadProfileBoilerFuel"]["year_one_boiler_fuel_load_series_mmbtu_per_hr"]
        load_boiler_thermal = d["outputs"]["Scenario"]["Site"]["LoadProfileBoilerFuel"]["year_one_boiler_thermal_load_series_mmbtu_per_hr"]

        # Fuel/thermal **consumption**
        boiler_fuel = d["outputs"]["Scenario"]["Site"]["Boiler"]["year_one_boiler_fuel_consumption_series_mmbtu_per_hr"]
        newboiler_fuel = d["outputs"]["Scenario"]["Site"]["NewBoiler"]["year_one_boiler_fuel_consumption_series_mmbtu_per_hr"]
        steamturbine_thermal_in = d["outputs"]["Scenario"]["Site"]["SteamTurbine"]["year_one_thermal_consumption_series_mmbtu_per_hr"]

        # Check the electric_out/thermal_in efficiency/ratio of the steam turbine with a pre-calculated expected value 
        steamturbine_electric = d["outputs"]["Scenario"]["Site"]["SteamTurbine"]["year_one_electric_production_series_kw"] 
        net_electric_efficiency = sum(steamturbine_electric) / (sum(newboiler_fuel) * MMBTU_TO_KWH)
        self.assertAlmostEqual(net_electric_efficiency, 0.185, delta=0.02)  # Expected value from spreadsheet

        # TODO test how REopt does export and how it operates without loads (for FTM/export-only):
        """
         1) Financial.wholesale_rate_us_dollars_per_kwh (SteamTurbine.can_wholesale)
         2) Financial.wholesale_rate_above_site_load_us_dollars_per_kwh (SteamTurbine.can_export_beyond_site_load)
         3) What if there are zero electric loads?
         4) What if there are zero heating loads?

        """ 
