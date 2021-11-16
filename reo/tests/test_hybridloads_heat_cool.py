import json
from tastypie.test import ResourceTestCaseMixin
from django.test import TestCase
from reo.models import ModelManager
import numpy as np

post = {
        "Scenario": {
            "Site": {
            "latitude": 37.78,
            "longitude": -122.45,
            "LoadProfile": {
                # Assigned below
            },
            "LoadProfileBoilerFuel": {
                # Assigned below
            },
            "LoadProfileChillerThermal": {
                # Assigned below
            },
            "ElectricTariff": {
                "urdb_label": "5cef0a415457a33576f60fe2"
            },
            "FuelTariff": {
                "boiler_fuel_blended_annual_rates_us_dollars_per_mmbtu": 11.0,
            },
            "Boiler": {
                "existing_boiler_production_type_steam_or_hw": "hot_water",
                "boiler_efficiency": 0.8
            },
            "PV": {
                "min_kw": 0.0,
                "max_kw": 0.0
            },
            "Storage": {
                "min_kw": 0.0,
                "max_kw": 0.0,
                "min_kwh": 0.0,
                "max_kwh": 0.0
            }
        }}}

class HybridLoadsHeatCoolTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(HybridLoadsHeatCoolTest, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_heat_cool_energy_balance(self):
        """

        Check that hybrid loads for electric is working as expected, and heating and cooling work too

        """

        hospital_pct = 75.0
        hotel_pct = 100 - hospital_pct

        # Hospital only
        post["Scenario"]["Site"]["LoadProfile"]["annual_kwh"] = hospital_pct
        post["Scenario"]["Site"]["LoadProfile"]["doe_reference_name"] = "Hospital"
        post["Scenario"]["Site"]["LoadProfileBoilerFuel"]["annual_mmbtu"] = hospital_pct
        post["Scenario"]["Site"]["LoadProfileBoilerFuel"]["doe_reference_name"] = "Hospital"
        post["Scenario"]["Site"]["LoadProfileChillerThermal"]["doe_reference_name"] = "Hospital"

        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        lp_hospital = d['outputs']['Scenario']['Site']['LoadProfile']["year_one_electric_load_series_kw"]
        lpbf_hospital = d['outputs']['Scenario']['Site']['LoadProfileBoilerFuel']["year_one_boiler_fuel_load_series_mmbtu_per_hr"]
        lpct_hospital = d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['year_one_chiller_electric_load_series_kw']
        lpct_hospital_frac_of_total = [lpct_hospital[i] / lp_hospital[i] for i in range(len(lp_hospital))]

        # Hotel only
        post["Scenario"]["Site"]["LoadProfile"]["annual_kwh"] = hotel_pct
        post["Scenario"]["Site"]["LoadProfile"]["doe_reference_name"] = "LargeHotel"
        post["Scenario"]["Site"]["LoadProfileBoilerFuel"]["annual_mmbtu"] = hotel_pct
        post["Scenario"]["Site"]["LoadProfileBoilerFuel"]["doe_reference_name"] = "LargeHotel"
        post["Scenario"]["Site"]["LoadProfileChillerThermal"]["doe_reference_name"] = "LargeHotel"

        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        lp_largehotel = d['outputs']['Scenario']['Site']['LoadProfile']["year_one_electric_load_series_kw"]
        lpbf_largehotel = d['outputs']['Scenario']['Site']['LoadProfileBoilerFuel']["year_one_boiler_fuel_load_series_mmbtu_per_hr"]
        lpct_largehotel = d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['year_one_chiller_electric_load_series_kw']
        lpct_largehotel_frac_of_total = [lpct_largehotel[i] / lp_largehotel[i] for i in range(len(lp_largehotel))]

        # Hybrid mix of hospital and hotel
        annual_energy = hospital_pct + hotel_pct
        building_list = ["Hospital", "LargeHotel"]
        percent_share_list = [hospital_pct, hotel_pct]
        post["Scenario"]["Site"]["LoadProfile"]["annual_kwh"] = annual_energy
        post["Scenario"]["Site"]["LoadProfile"]["doe_reference_name"] = building_list
        post["Scenario"]["Site"]["LoadProfile"]["percent_share"] = percent_share_list
        
        post["Scenario"]["Site"]["LoadProfileBoilerFuel"]["annual_mmbtu"] = annual_energy
        post["Scenario"]["Site"]["LoadProfileBoilerFuel"]["doe_reference_name"] = building_list
        post["Scenario"]["Site"]["LoadProfileBoilerFuel"]["percent_share"] = percent_share_list

        # API should now use a weighted fraction of total electric profile if no annual_tonhour is provided
        post["Scenario"]["Site"]["LoadProfileChillerThermal"]["doe_reference_name"] = building_list
        post["Scenario"]["Site"]["LoadProfileChillerThermal"]["percent_share"] = percent_share_list

        # Add GHP to the scenario so we can parse Space Heating (GHP-servable) Vs DHW (not GHP-servable) for hybrid loads
        post["Scenario"]["Site"]["GHP"] = {}
        post["Scenario"]["Site"]["GHP"]["building_sqft"] = 100000.0
        post["Scenario"]["Site"]["GHP"]["require_ghp_purchase"] = True

        resp = self.get_response(data=post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        lp_combined = d['outputs']['Scenario']['Site']['LoadProfile']["year_one_electric_load_series_kw"]
        lpbf_combined = d['outputs']['Scenario']['Site']['LoadProfileBoilerFuel']["year_one_boiler_fuel_load_series_mmbtu_per_hr"]
        lpct_combined = d['outputs']['Scenario']['Site']['LoadProfileChillerThermal']['year_one_chiller_electric_load_series_kw']

        # Check that the combined/hybrid load is the same as the sum of the individual loads in each timestep
        self.assertAlmostEqual(0.0, sum([lp_combined[i] - (lp_hospital[i] + lp_largehotel[i]) for i in range(len(lp_combined))]), places=3)
        self.assertAlmostEqual(0.0, sum([lpbf_combined[i] - (lpbf_hospital[i] + lpbf_largehotel[i]) for i in range(len(lpbf_combined))]), places=3)
        
        # Check that the Space Heating Vs DHW is scaling correctly with hybrid blends of buildings
        # Values below are from input_files/LoadProfiles [space/dhw]_annual_mmbtu.json
        default_hospital_space_mmbtu = 11570.9155
        default_largehotel_space_mmbtu = 1713.362967
        default_hospital_dhw_mmbtu = 671.40531
        default_largehotel_dhw_mmbtu = 6241.842643
        default_hospital_total_mmbtu = default_hospital_space_mmbtu + default_hospital_dhw_mmbtu
        default_largehotel_total_mmbtu = default_largehotel_space_mmbtu + default_largehotel_dhw_mmbtu

        # Check expected space heating with the heating load which GHP served
        expected_space_heating_mmbtu = annual_energy * (default_hospital_space_mmbtu / default_hospital_total_mmbtu * hospital_pct / 100.0 + 
                                                  default_largehotel_space_mmbtu / default_largehotel_total_mmbtu * hotel_pct / 100.0)

        ghp_space_heating_served = np.array(d['outputs']['Scenario']['Site']['GHP']['ghpghx_chosen_outputs']['heating_thermal_load_mmbtu_per_hr']) / \
                                            d['inputs']['Scenario']['Site']['Boiler']['boiler_efficiency']

        self.assertAlmostEqual(expected_space_heating_mmbtu, sum(ghp_space_heating_served), places=3)

        # Check that the cooling load is the weighted average of the default CRB fraction of total electric profiles
        lpct_combined_expected = [lp_combined[i] * (lpct_hospital_frac_of_total[i] * hospital_pct / 100.0 + 
                                                    lpct_largehotel_frac_of_total[i] * hotel_pct / 100.0)
                                                    for i in range(len(lp_combined))]
        self.assertAlmostEqual(0.0, sum([lpct_combined_expected[i] - lpct_combined[i] for i in range(len(lpct_combined))]), places=3)

        




