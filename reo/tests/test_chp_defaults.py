import json
from django.test import SimpleTestCase
from reo.validators import ValidateNestedInput
from reo.src.techs import CHP, Boiler, ElectricChiller, AbsorptionChiller

class TestCHPDefaults(SimpleTestCase): 
    """
    These tests are meant to confirm that reo.validators is
    assigning the correct CHP defaults with the dependencies on other inputs, such as Boiler. 
    Make sure reo.validators is consistent with the chp_defaults view which is what the Webtool shows users.
    CHP cost and performance depends on 1) CHP.prime_mover, 2) CHP.size_class, 3) Boiler.existing_boiler_production_type_steam_or_hw
    
    Chiller defaults (Later, TBD) - maybe make this a separate test class and file, but some dependencies on CHP
    Make sure that ElectricChiller and AbsorptionChiller defaults and dependencies are handled correctly
    AbsorptionChiller.chiller_cop depends on Boiler.existing_boiler_production_type_steam_or_hw and peak and
    the peak cooling capacity of the site (installed_cost also depends on peak capacity)
    ElectricChiller.chiller_cop depends on peak cooling capacity of the site

    """

    # CHP_post = {
    #     "prime_mover": "recip_engine",
    #     "min_kw": 100.0,
    #     "max_kw": 800.0,
    #     "min_allowable_kw": 15.0,
    #     "installed_cost_us_dollars_per_kw": 2416.7,
    #     "om_cost_us_dollars_per_kw": 149.8,
    #     "om_cost_us_dollars_per_kwh": 0.0,
    #     "om_cost_us_dollars_per_hr_per_kw_rated": 0.0,
    #     "elec_effic_full_load": 0.3573,
    #     "elec_effic_half_load": 0.3216,
    #     "min_turn_down_pct": 0.5,
    #     "thermal_effic_full_load": 0.4418,
    #     "thermal_effic_half_load": 0.4664,
    #     "use_default_derate": true,
    #     "max_derate_factor": 1.0,
    #     "derate_start_temp_degF": 95.0,
    #     "derate_slope_pct_per_degF": 0.008,
    #     "macrs_option_years": 0,
    #     "macrs_bonus_pct": 0.0,
    #     "macrs_itc_reduction": 0.0,
    #     "federal_itc_pct": 0.0,
    #     "state_ibi_pct": 0.0,
    #     "state_ibi_max_us_dollars": 0.0,
    #     "utility_ibi_pct": 0.0,
    #     "utility_ibi_max_us_dollars": 0.0,
    #     "federal_rebate_us_dollars_per_kw": 0.0,
    #     "state_rebate_us_dollars_per_kw": 0.0,
    #     "state_rebate_max_us_dollars": 0.0,
    #     "utility_rebate_us_dollars_per_kw": 0.0,
    #     "utility_rebate_max_us_dollars": 0.0,
    #     "pbi_us_dollars_per_kwh": 0.0,
    #     "pbi_max_us_dollars": 0.0,
    #     "pbi_years": 0.0,
    #     "pbi_system_max_kw": 0.0,
    #     "emissions_factor_lb_CO2_per_mmbtu": 116.9
    #   }
    # Boiler_post = {
    #     "min_mmbtu_per_hr": 0.0,
    #     "max_mmbtu_per_hr": 1000000000.0,
    #     "existing_boiler_production_type_steam_or_hw": "hot_water",
    #     "boiler_efficiency": 0.8
    #   }

    def setUp(self):
        super(TestCHPDefaults, self).setUp()
        self.views_chp_defaults_base = '/v1/chp_defaults/'

    def get_chp_defaults_response(self, params_dict):
        response = self.client.get(self.views_chp_defaults_base, data=params_dict)
        return response
    
    @staticmethod
    def get_validator(post):
        validator = ValidateNestedInput(post)
        return validator

    def test_chp_defaults(self):
        test_params_dict = {"prime_mover": "recip_engine",
                        "size_class": 3,
                        "existing_boiler_production_type_steam_or_hw": "hot_water",
                        "year": 2017}
        
        resp = self.get_chp_defaults_response(params_dict=test_params_dict)
        r = json.loads(resp.content)
        dummy = 3
