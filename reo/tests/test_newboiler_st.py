# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
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
