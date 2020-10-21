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
from reo.src.data_manager import big_number
from reo.src.pvwatts import PVWatts
from reo.src.wind import WindSAMSDK
from reo.src.incentives import Incentives, IncentivesNoProdBased
from reo.models import ModelManager
import numpy as np


class Tech(object):
    """
    base class for REopt energy generation technology
    """

    def __init__(self, min_kw=0, max_kw=big_number, installed_cost_us_dollars_per_kw=big_number,
                 om_cost_us_dollars_per_kw=0.0, *args, **kwargs):

        self.min_kw = min_kw
        self.max_kw = max_kw
        self.installed_cost_us_dollars_per_kw = installed_cost_us_dollars_per_kw
        self.om_cost_us_dollars_per_kw = om_cost_us_dollars_per_kw

        self.loads_served = ['retail', 'wholesale', 'export', 'storage', 'boiler', 'tes']
        self.nmil_regime = None
        self.reopt_class = ""
        self.derate = 1.0
        self.is_chp = False
        self.is_hot = False
        self.is_cool = False
        self.derate = 1
        self.acres_per_kw = None  # for land constraints
        self.kw_per_square_foot = None  # for roof constraints

        self.kwargs = kwargs

    @property
    def prod_factor(self):
        """
        Production Factor.  Combination of resource, efficiency, and availability.
        :return: prod_factor
        """
        return None

    def can_serve(self, load):
        if load in self.loads_served:
            return True
        return False


class Util(Tech):

    def __init__(self, dfm, outage_start_hour=None, outage_end_hour=None):
        super(Util, self).__init__(max_kw=12000000)

        self.outage_start_hour = outage_start_hour
        self.outage_end_hour = outage_end_hour
        self.loads_served = ['retail', 'storage']
        self.derate = 0.0
        self.n_timesteps = dfm.n_timesteps

        dfm.add_util(self)

    @property
    def prod_factor(self):

        grid_prod_factor = [1.0 for _ in range(self.n_timesteps)]

        if self.outage_start_hour is not None and self.outage_end_hour is not None:  # "turn off" grid resource
            grid_prod_factor[self.outage_start_hour:self.outage_end_hour] = [0]*(self.outage_end_hour - self.outage_start_hour)

        return grid_prod_factor


class PV(Tech):
    array_type_to_tilt_angle = {
        0: 0,  # ground-mount fixed array type's tilt should be equal to the latitude
        1: 10,
        2: 0,
        3: 0,
        4: 0
    }

    def __init__(self, dfm, degradation_pct, time_steps_per_hour=1, acres_per_kw=6e-3, kw_per_square_foot=0.01, existing_kw=0.0, tilt=0.537, azimuth=180, pv_number=1, location='both', prod_factor_series_kw=None, **kwargs):
        super(PV, self).__init__(**kwargs)

        self.degradation_pct = degradation_pct
        self.nmil_regime = 'BelowNM'
        self.reopt_class = 'PV' + str(pv_number)
        self.acres_per_kw = acres_per_kw
        self.kw_per_square_foot = kw_per_square_foot
        self.time_steps_per_hour = time_steps_per_hour
        self.incentives = Incentives(**kwargs)
        self.tilt = tilt
        self.azimuth = azimuth
        self.pvwatts_prod_factor = None
        self.existing_kw = existing_kw
        self.prod_factor_series_kw = prod_factor_series_kw
        self.tech_name = 'pv' + str(pv_number)
        self.location = location

        # if user hasn't entered the tilt (default value is 0.537), tilt value gets assigned based on array_type
        if self.tilt == 0.537:
            if kwargs.get('array_type') == 0:  # 0 are Ground Mount Fixed (Open Rack) arrays, we assume an optimal tilt
                """
                start assuming the site is in the northern hemisphere, set the tilt to the latitude and leave the 
                default azimuth of 180 (unless otherwise specified)
                """
                self.tilt = kwargs.get('latitude')
                if kwargs.get('latitude') < 0:
                    """
                    if the site is in the southern hemisphere, now set the tilt to the positive latitude value and 
                    change the azimuth to 0. Also update kwargs going forward so they get saved to the database later 
                    show up in final results
                    """
                    self.tilt = -1 * self.tilt
                    self.azimuth = 0
            else:  # All other tilts come from lookup table included in the array_type_to_tilt_angle dictionary above
                self.tilt = PV.array_type_to_tilt_angle[kwargs.get('array_type')]

        self.pvwatts = PVWatts(time_steps_per_hour=self.time_steps_per_hour, azimuth=self.azimuth, tilt=self.tilt, **self.kwargs)

        dfm.add_pv(self)

    @property
    def prod_factor(self):
        if self.prod_factor_series_kw is None:
            if self.pvwatts_prod_factor is None:
                self.pvwatts_prod_factor = self.pvwatts.pv_prod_factor
            return self.pvwatts_prod_factor
        else:
            return self.prod_factor_series_kw

    @property
    def station_location(self):
        station = (self.pvwatts.response['station_info']['lat'],
                   self.pvwatts.response['station_info']['lon'],
                   round(self.pvwatts.response['station_info']['distance']/1000,1))
        return station


class Wind(Tech):
    size_class_to_hub_height = {
        'residential': 20,
        'commercial': 40,
        'medium': 60,  # Owen Roberts provided 50m for medium size_class, but Wind Toolkit has increments of 20m
        'large': 80,
    }
    size_class_to_installed_cost = {
        'residential': 11950,
        'commercial': 7390,
        'medium': 4440,
        'large': 3450,
    }

    size_class_to_itc_incentives = {
        'residential': 0.3,
        'commercial': 0.3,
        'medium': 0.12,
        'large': 0.12,
    }

    def __init__(self, dfm, inputs_path, acres_per_kw=.03, time_steps_per_hour=1, prod_factor_series_kw=None, **kwargs):
        super(Wind, self).__init__(**kwargs)

        self.path_inputs = inputs_path
        self.nmil_regime = 'BelowNM'
        self.reopt_class = 'WIND'
        self.acres_per_kw = acres_per_kw
        self.hub_height_meters = Wind.size_class_to_hub_height[kwargs['size_class']]
        self.time_steps_per_hour = time_steps_per_hour
        self.incentives = Incentives(**kwargs)
        self.installed_cost_us_dollars_per_kw = kwargs.get('installed_cost_us_dollars_per_kw')
        self.prod_factor_series_kw = prod_factor_series_kw

        # if user hasn't entered the federal itc, itc value gets assigned based on size_class
        if self.incentives.federal.itc == 0.3:
            self.incentives.federal.itc = Wind.size_class_to_itc_incentives[kwargs.get('size_class')]

        # if user hasn't entered the installed cost per kw, it gets assigned based on size_class
        if kwargs.get('installed_cost_us_dollars_per_kw') == 3013:
            self.installed_cost_us_dollars_per_kw = Wind.size_class_to_installed_cost[kwargs.get('size_class')]

        self.sam_prod_factor = None
        dfm.add_wind(self)

    @property
    def prod_factor(self):
        """
        Pass resource_meters_per_sec to SAM SDK to get production factor
        :return: wind turbine production factor for 1kW system for 1 year with length = 8760 * time_steps_per_hour
        """
        if self.prod_factor_series_kw is None:
            if self.sam_prod_factor is None:
                sam = WindSAMSDK(path_inputs=self.path_inputs, hub_height_meters=self.hub_height_meters,
                                 time_steps_per_hour=self.time_steps_per_hour, **self.kwargs)
                self.sam_prod_factor = sam.wind_prod_factor()
            return self.sam_prod_factor
        else:
            return self.prod_factor_series_kw


class Generator(Tech):

    def __init__(self, dfm, run_uuid, min_kw, max_kw, existing_kw, fuel_slope_gal_per_kwh, fuel_intercept_gal_per_hr,
                 fuel_avail_gal, min_turn_down_pct, outage_start_hour=None, outage_end_hour=None, time_steps_per_hour=1,
                 fuel_avail_before_outage_pct=1, emissions_factor_lb_CO2_per_gal=None, **kwargs):
        super(Generator, self).__init__(min_kw=min_kw, max_kw=max_kw, **kwargs)
        """
        super class init for generator is not unique anymore as we are now allowing users to define min/max sizes;
        and include diesel generator's size as optimization decision variable.
        
        Note that default burn rate, slope, and min/max sizes are handled in ValidateNestedInput.
        """

        self.fuel_slope = fuel_slope_gal_per_kwh
        self.fuel_intercept = fuel_intercept_gal_per_hr
        self.fuel_avail = fuel_avail_gal
        self.min_turn_down = min_turn_down_pct
        self.reopt_class = 'GENERATOR'
        self.outage_start_hour = outage_start_hour
        self.outage_end_hour = outage_end_hour
        self.time_steps_per_hour = time_steps_per_hour
        self.generator_only_runs_during_grid_outage = kwargs['generator_only_runs_during_grid_outage']
        self.fuel_avail_before_outage_pct = fuel_avail_before_outage_pct
        self.generator_sells_energy_back_to_grid = kwargs['generator_sells_energy_back_to_grid']
        self.diesel_fuel_cost_us_dollars_per_gallon = kwargs['diesel_fuel_cost_us_dollars_per_gallon']
        self.derate = 0.0
        self.loads_served = ['retail', 'storage']
        self.incentives = Incentives(**kwargs)
        if max_kw < min_kw:
            min_kw = max_kw
        self.min_kw = min_kw
        self.max_kw = max_kw
        self.existing_kw = existing_kw
        self.emissions_factor_lb_CO2_per_gal = emissions_factor_lb_CO2_per_gal

        # no net-metering for gen so it can only sell in "wholesale" bin (and not "export" bin)
        if self.generator_sells_energy_back_to_grid:
            self.loads_served.append('wholesale')

        dfm.add_generator(self)

    @property
    def prod_factor(self):
        gen_prod_factor = [0.0 for _ in range(8760*self.time_steps_per_hour)]

        if self.generator_only_runs_during_grid_outage:
            if self.outage_start_hour is not None and self.outage_end_hour is not None:
                gen_prod_factor[self.outage_start_hour:self.outage_end_hour] \
                    = [1]*(self.outage_end_hour - self.outage_start_hour)

        else:
            gen_prod_factor = [1] * len(gen_prod_factor)

        return gen_prod_factor

    @staticmethod
    def default_fuel_burn_rate(size_kw):
        """
        Based off of size_kw, we have default (fuel_slope_gal_per_kwh, fuel_intercept_gal_per_hr) pairs
        :return: (fuel_slope_gal_per_kwh, fuel_intercept_gal_per_hr)
        """
        if size_kw <= 40:
            m = 0.068
            b = 0.0125
        elif size_kw <= 80:
            m = 0.066
            b = 0.0142
        elif size_kw <= 150:
            m = 0.0644
            b = 0.0095
        elif size_kw <= 250:
            m = 0.0648
            b = 0.0067
        elif size_kw <= 750:
            m = 0.0656
            b = 0.0048
        elif size_kw <= 1500:
            m = 0.0657
            b = 0.0043
        else:
            m = 0.0657
            b = 0.004
        return m, b


class CHP(Tech):
    """
    Includes calcs for converting user-input electric efficiency and thermal recovery fraction to coefficients
    useable for JuMP (e.g. fuel burn rate in MMBtu/hr/kW_rated (y-intercept)

    """
    # Default data, created from input_files.CHP.chp_input_defaults_processing, copied from chp_default_data.json
    prime_mover_defaults_all = {
                              "recip_engine": {
                                "installed_cost_us_dollars_per_kw": [
                                  [
                                    3300.0 ,
                                    1430.0
                                  ] ,
                                  [
                                    3300.0 ,
                                    2900.0
                                  ] ,
                                  [
                                    2900.0 ,
                                    2700.0
                                  ] ,
                                  [
                                    2700.0 ,
                                    2370.0
                                  ] ,
                                  [
                                    2370.0 ,
                                    1800.0
                                  ] ,
                                  [
                                    1800.0 ,
                                    1430.0
                                  ]
                                ] ,
                                "tech_size_for_cost_curve": [
                                  [
                                    30 ,
                                    9300
                                  ] ,
                                  [
                                    30 ,
                                    100
                                  ] ,
                                  [
                                    100 ,
                                    630
                                  ] ,
                                  [
                                    630 ,
                                    1140
                                  ] ,
                                  [
                                    1140 ,
                                    3300
                                  ] ,
                                  [
                                    3300 ,
                                    9300
                                  ]
                                ] ,
                                "om_cost_us_dollars_per_kw": [
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0
                                ] ,
                                "om_cost_us_dollars_per_kwh": [
                                  0.019694444444444445 ,
                                  0.026583333333333334 ,
                                  0.0225 ,
                                  0.02 ,
                                  0.0175 ,
                                  0.0125
                                ] ,
                                "om_cost_us_dollars_per_hr_per_kw_rated": [
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0
                                ] ,
                                "elec_effic_full_load": [
                                  0.3573333333333333 ,
                                  0.2975 ,
                                  0.3205 ,
                                  0.3605 ,
                                  0.39249999999999996 ,
                                  0.414
                                ] ,
                                "elec_effic_half_load": [
                                  0.3573333333333333 ,
                                  0.2975 ,
                                  0.3205 ,
                                  0.3605 ,
                                  0.39249999999999996 ,
                                  0.414
                                ] ,
                                "thermal_effic_full_load": [
                                  0.4418333333333333 ,
                                  0.516 ,
                                  0.4925 ,
                                  0.4415 ,
                                  0.40800000000000003 ,
                                  0.368
                                ] ,
                                "thermal_effic_half_load": [
                                  0.4418333333333333 ,
                                  0.516 ,
                                  0.4925 ,
                                  0.4415 ,
                                  0.40800000000000003 ,
                                  0.368
                                ] ,
                                "min_allowable_kw": [
                                  15.0 ,
                                  15.0 ,
                                  50.0 ,
                                  315.0 ,
                                  570.0 ,
                                  1650.0
                                ] ,
                                "min_kw": [
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0
                                ] ,
                                "max_kw": [
                                  10000 ,
                                  10000 ,
                                  10000 ,
                                  10000 ,
                                  10000 ,
                                  10000
                                ] ,
                                "min_turn_down_pct": [
                                  0.5 ,
                                  0.5 ,
                                  0.5 ,
                                  0.5 ,
                                  0.5 ,
                                  0.5
                                ] ,
                                "max_derate_factor": [
                                  1.0 ,
                                  1.0 ,
                                  1.0 ,
                                  1.0 ,
                                  1.0 ,
                                  1.0
                                ] ,
                                "derate_start_temp_degF": [
                                  95 ,
                                  95 ,
                                  95 ,
                                  95 ,
                                  95 ,
                                  95
                                ] ,
                                "derate_slope_pct_per_degF": [
                                  0.008 ,
                                  0.008 ,
                                  0.008 ,
                                  0.008 ,
                                  0.008 ,
                                  0.008
                                ]
                              } ,
                              "micro_turbine": {
                                "installed_cost_us_dollars_per_kw": [
                                  [
                                    3600.0 ,
                                    2500.0
                                  ] ,
                                  [
                                    3600.0 ,
                                    3220.0
                                  ] ,
                                  [
                                    3220.0 ,
                                    3150.0
                                  ] ,
                                  [
                                    3150.0 ,
                                    2500.0
                                  ]
                                ] ,
                                "tech_size_for_cost_curve": [
                                  [
                                    30 ,
                                    950
                                  ] ,
                                  [
                                    30 ,
                                    60
                                  ] ,
                                  [
                                    60 ,
                                    190
                                  ] ,
                                  [
                                    190 ,
                                    950
                                  ]
                                ] ,
                                "om_cost_us_dollars_per_kw": [
                                  0 ,
                                  0 ,
                                  0 ,
                                  0
                                ] ,
                                "om_cost_us_dollars_per_kwh": [
                                  0.0176 ,
                                  0.026000000000000002 ,
                                  0.021 ,
                                  0.012000000000000002
                                ] ,
                                "om_cost_us_dollars_per_hr_per_kw_rated": [
                                  0 ,
                                  0 ,
                                  0 ,
                                  0
                                ] ,
                                "elec_effic_full_load": [
                                  0.2658 ,
                                  0.2405 ,
                                  0.264 ,
                                  0.2826666666666667
                                ] ,
                                "elec_effic_half_load": [
                                  0.2658 ,
                                  0.2405 ,
                                  0.264 ,
                                  0.2826666666666667
                                ] ,
                                "thermal_effic_full_load": [
                                  0.4202 ,
                                  0.46950000000000003 ,
                                  0.4225 ,
                                  0.3873333333333333
                                ] ,
                                "thermal_effic_half_load": [
                                  0.4202 ,
                                  0.46950000000000003 ,
                                  0.4225 ,
                                  0.3873333333333333
                                ] ,
                                "min_allowable_kw": [
                                  21.0 ,
                                  21.0 ,
                                  42.0 ,
                                  133.0
                                ] ,
                                "min_kw": [
                                  0 ,
                                  0 ,
                                  0 ,
                                  0
                                ] ,
                                "max_kw": [
                                  1000 ,
                                  1000 ,
                                  1000 ,
                                  1000
                                ] ,
                                "min_turn_down_pct": [
                                  0.3 ,
                                  0.3 ,
                                  0.3 ,
                                  0.3
                                ] ,
                                "max_derate_factor": [
                                  1.0 ,
                                  1.0 ,
                                  1.0 ,
                                  1.0
                                ] ,
                                "derate_start_temp_degF": [
                                  59 ,
                                  59 ,
                                  59 ,
                                  59
                                ] ,
                                "derate_slope_pct_per_degF": [
                                  0.012 ,
                                  0.012 ,
                                  0.012 ,
                                  0.012
                                ]
                              } ,
                              "combustion_turbine": {
                                "installed_cost_us_dollars_per_kw": [
                                  [
                                    4480.0 ,
                                    1430.0
                                  ] ,
                                  [
                                    4480.0 ,
                                    3900.0
                                  ] ,
                                  [
                                    3900.0 ,
                                    3320.0
                                  ] ,
                                  [
                                    3320.0 ,
                                    2817.0
                                  ] ,
                                  [
                                    2817.0 ,
                                    2017.0
                                  ] ,
                                  [
                                    2017.0 ,
                                    1750.0
                                  ] ,
                                  [
                                    1750.0 ,
                                    1430.0
                                  ]
                                ] ,
                                "tech_size_for_cost_curve": [
                                  [
                                    950 ,
                                    20000
                                  ] ,
                                  [
                                    950 ,
                                    1800
                                  ] ,
                                  [
                                    1800 ,
                                    3300
                                  ] ,
                                  [
                                    3300 ,
                                    5400
                                  ] ,
                                  [
                                    5400 ,
                                    7500
                                  ] ,
                                  [
                                    7500 ,
                                    14000
                                  ] ,
                                  [
                                    14000 ,
                                    20000
                                  ]
                                ] ,
                                "om_cost_us_dollars_per_kw": [
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0
                                ] ,
                                "om_cost_us_dollars_per_kwh": [
                                  0.012285714285714283 ,
                                  0.014499999999999999 ,
                                  0.0135 ,
                                  0.013000000000000001 ,
                                  0.0125 ,
                                  0.011 ,
                                  0.0095
                                ] ,
                                "om_cost_us_dollars_per_hr_per_kw_rated": [
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0
                                ] ,
                                "elec_effic_full_load": [
                                  0.26599999999999996 ,
                                  0.2175 ,
                                  0.23099999999999998 ,
                                  0.2525 ,
                                  0.2795 ,
                                  0.2955 ,
                                  0.3155
                                ] ,
                                "elec_effic_half_load": [
                                  0.26599999999999996 ,
                                  0.2175 ,
                                  0.23099999999999998 ,
                                  0.2525 ,
                                  0.2795 ,
                                  0.2955 ,
                                  0.3155
                                ] ,
                                "thermal_effic_full_load": [
                                  0.4222857142857143 ,
                                  0.4605 ,
                                  0.4515 ,
                                  0.4255 ,
                                  0.42500000000000004 ,
                                  0.4075 ,
                                  0.3855
                                ] ,
                                "thermal_effic_half_load": [
                                  0.4222857142857143 ,
                                  0.4605 ,
                                  0.4515 ,
                                  0.4255 ,
                                  0.42500000000000004 ,
                                  0.4075 ,
                                  0.3855
                                ] ,
                                "min_allowable_kw": [
                                  950.0 ,
                                  950.0 ,
                                  1800.0 ,
                                  3300.0 ,
                                  5400.0 ,
                                  7500.0 ,
                                  14000.0
                                ] ,
                                "min_kw": [
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0 ,
                                  0
                                ] ,
                                "max_kw": [
                                  20000 ,
                                  20000 ,
                                  20000 ,
                                  20000 ,
                                  20000 ,
                                  20000 ,
                                  20000
                                ] ,
                                "min_turn_down_pct": [
                                  0.5 ,
                                  0.5 ,
                                  0.5 ,
                                  0.5 ,
                                  0.5 ,
                                  0.5 ,
                                  0.5
                                ] ,
                                "max_derate_factor": [
                                  1.1 ,
                                  1.1 ,
                                  1.1 ,
                                  1.1 ,
                                  1.1 ,
                                  1.1 ,
                                  1.1
                                ] ,
                                "derate_start_temp_degF": [
                                  59 ,
                                  59 ,
                                  59 ,
                                  59 ,
                                  59 ,
                                  59 ,
                                  59
                                ] ,
                                "derate_slope_pct_per_degF": [
                                  0.012 ,
                                  0.012 ,
                                  0.012 ,
                                  0.012 ,
                                  0.012 ,
                                  0.012 ,
                                  0.012
                                ]
                              } ,
                              "fuel_cell": {
                                "installed_cost_us_dollars_per_kw": [
                                  [
                                    10000.0 ,
                                    3800.0
                                  ] ,
                                  [
                                    10000.0 ,
                                    10000.0
                                  ] ,
                                  [
                                    10000.0 ,
                                    4600.0
                                  ] ,
                                  [
                                    4600.0 ,
                                    3800.0
                                  ]
                                ] ,
                                "tech_size_for_cost_curve": [
                                  [
                                    30 ,
                                    9300
                                  ] ,
                                  [
                                    30 ,
                                    320
                                  ] ,
                                  [
                                    320 ,
                                    1400
                                  ] ,
                                  [
                                    1400 ,
                                    9300
                                  ]
                                ] ,
                                "om_cost_us_dollars_per_kw": [
                                  0 ,
                                  0 ,
                                  0 ,
                                  0
                                ] ,
                                "om_cost_us_dollars_per_kwh": [
                                  0.04 ,
                                  0.045 ,
                                  0.042499999999999996 ,
                                  0.035
                                ] ,
                                "om_cost_us_dollars_per_hr_per_kw_rated": [
                                  0 ,
                                  0 ,
                                  0 ,
                                  0
                                ] ,
                                "elec_effic_full_load": [
                                  0.425 ,
                                  0.425 ,
                                  0.425 ,
                                  0.425
                                ] ,
                                "elec_effic_half_load": [
                                  0.425 ,
                                  0.425 ,
                                  0.425 ,
                                  0.425
                                ] ,
                                "thermal_effic_full_load": [
                                  0.32549999999999996 ,
                                  0.32799999999999996 ,
                                  0.32549999999999996 ,
                                  0.32299999999999995
                                ] ,
                                "thermal_effic_half_load": [
                                  0.32549999999999996 ,
                                  0.32799999999999996 ,
                                  0.32549999999999996 ,
                                  0.32299999999999995
                                ] ,
                                "min_allowable_kw": [
                                  15.0 ,
                                  15.0 ,
                                  160.0 ,
                                  700.0
                                ] ,
                                "min_kw": [
                                  0 ,
                                  0 ,
                                  0 ,
                                  0
                                ] ,
                                "max_kw": [
                                  5000 ,
                                  5000 ,
                                  5000 ,
                                  5000
                                ] ,
                                "min_turn_down_pct": [
                                  0.3 ,
                                  0.3 ,
                                  0.3 ,
                                  0.3
                                ] ,
                                "max_derate_factor": [
                                  1.0 ,
                                  1.0 ,
                                  1.0 ,
                                  1.0
                                ] ,
                                "derate_start_temp_degF": [
                                  59 ,
                                  59 ,
                                  59 ,
                                  59
                                ] ,
                                "derate_slope_pct_per_degF": [
                                  0.008 ,
                                  0.008 ,
                                  0.008 ,
                                  0.008
                                ]
                              }
                                }

    # Lower and upper bounds for size classes - Class 0 is the total average across entire range of data
    class_bounds = {"recip_engine": [(30, 9300), (30, 100), (100, 630), (630, 1140), (1140, 3300), (3300, 9300)],
                    "micro_turbine": [(30, 950), (30, 60), (60, 190), (190, 950)],
                    "combustion_turbine": [(950, 20000), (950, 1800), (1800, 3300), (3300, 5400), (5400, 7500),
                                           (7500, 14000), (14000, 20000)],
                    "fuel_cell": [(30, 9300), (30, 320), (320, 1400), (1400, 9300)]}

    # The default CHP size class, currently set to size_class 0 which is the average values across the entire range of data (i.e. all size classes)
    default_chp_size_class = {"recip_engine": 0,
                              "micro_turbine": 0,
                              "combustion_turbine": 0,
                              "fuel_cell": 0}

    def __init__(self, dfm, run_uuid, existing_boiler_production_type_steam_or_hw, oa_temp_degF, site_elevation_ft,
                 time_steps_per_hour=1, **kwargs):
        super(CHP, self).__init__()

        self.prime_mover = kwargs.get('prime_mover')
        self.size_class = kwargs.get('size_class')
        self.existing_boiler_production_type_steam_or_hw = existing_boiler_production_type_steam_or_hw
        self.reopt_class = 'CHP'
        self.is_chp = True
        self.time_steps_per_hour = time_steps_per_hour
        self.derate = 1  # Need to rectify this legacy derate, maybe remove this and replace if no needed (NM/IL?)
        self.loads_served = ['retail', 'wholesale', 'export', 'storage', 'boiler', 'tes']
        self.incentives = Incentives(**kwargs)

        # All of these attributes are assigned based on defaults in validators.py or they should all be in the inputs
        self.min_kw = kwargs['min_kw']
        self.max_kw = kwargs['max_kw']
        self.installed_cost_us_dollars_per_kw = kwargs['installed_cost_us_dollars_per_kw']
        self.tech_size_for_cost_curve = kwargs.get('tech_size_for_cost_curve')
        self.om_cost_us_dollars_per_kw = kwargs['om_cost_us_dollars_per_kw']
        self.om_cost_us_dollars_per_kwh = kwargs['om_cost_us_dollars_per_kwh']
        self.om_cost_us_dollars_per_hr_per_kw_rated = kwargs['om_cost_us_dollars_per_hr_per_kw_rated']
        self.elec_effic_full_load = kwargs['elec_effic_full_load']
        self.elec_effic_half_load = kwargs['elec_effic_half_load']
        self.thermal_effic_full_load = kwargs['thermal_effic_full_load']
        self.thermal_effic_half_load = kwargs['thermal_effic_half_load']
        self.min_turn_down_pct = kwargs['min_turn_down_pct']
        self.min_allowable_kw = kwargs['min_allowable_kw']
        self.use_default_derate = kwargs['use_default_derate']
        self.max_derate_factor = kwargs['max_derate_factor']
        self.derate_start_temp_degF = kwargs['derate_start_temp_degF']
        self.derate_slope_pct_per_degF = kwargs['derate_slope_pct_per_degF']

        self.fuel_burn_slope, self.fuel_burn_intercept, self.thermal_prod_slope, self.thermal_prod_intercept = \
                    self.convert_performance_params(oa_temp_degF)
        self.chp_power_derate = self.calculate_chp_power_derate(site_elevation_ft, oa_temp_degF)

        dfm.add_chp(self)

    def calculate_chp_power_derate(self, site_elevation_ft, oa_temp_degF):

        if self.use_default_derate:
            # TODO: Use either site altitude OR derate_max, depending on which, if any, are input. VALIDATORS.PY to handle this!
            # TODO: implement derate factor array based on input temperature profile, with derate_max from above TODO
            chp_power_derate = [1.0 for _ in range(8760 * self.time_steps_per_hour)]  # initialize
            oa_temp_degF = np.array(oa_temp_degF)

            if self.prime_mover == 'micro_turbine':
            # create the de-rate curve for the corresponding elevation
                # 72 F at 0 ft elevation
                p1 = -0.000000000039870
                p2 = 0.000001163139968
                p3 = -0.011086702413053
                p4 = 72.568538058825453
                self.derate_start_temp_degF = self.derate_start_temp_degF * \
                        ((p1*site_elevation_ft**3 + p2*site_elevation_ft**2 + p3*site_elevation_ft + p4) / p4)
                # 0.5 % per F at 0 ft elevation
                p1 =  0.000000153005769
                p2 = -0.005127272115385
                self.derate_slope_pct_per_degF = self.derate_slope_pct_per_degF * \
                                        ((p1*site_elevation_ft + p2) / p2)
                # 1 at 0 ft elevation
                p1 = -0.000000003072106
                p2 = 0.000005739931623
                p3 = 1.010408869405444
                if site_elevation_ft <= 3000: # [ft]
                    self.max_derate_factor = self.max_derate_factor*1 # (equal to 1)
                else:
                    self.max_derate_factor = self.max_derate_factor * \
                        (( p1*site_elevation_ft**2 + p2*site_elevation_ft + p3) / p3)

                #calculate hourly power derate as a function of temperature
                for i in range(8760 * self.time_steps_per_hour): #can an if statement be in that other type of looping method??
                    if oa_temp_degF[i] <= self.derate_start_temp_degF:
                        chp_power_derate[i] = 1.0 * self.max_derate_factor
                    else:
                        chp_power_derate[i] = 1.0 * self.max_derate_factor - \
                                              self.derate_slope_pct_per_degF * (oa_temp_degF[i] - self.derate_start_temp_degF)
            elif self.prime_mover == 'recip_engine':
                if self.size_class == 1:
                    # de-rate is only a function of elevation for naturally aspirated engines (approx 30-100 kW)
                    self.derate_start_temp_degF = self.derate_start_temp_degF * 1
                    self.derate_slope_pct_per_degF = self.derate_slope_pct_per_degF * 1
                    self.max_derate_factor = self.max_derate_factor * 1
                    for i in range(8760 * self.time_steps_per_hour):
                        if oa_temp_degF[i] <= self.derate_start_temp_degF:
                            chp_power_derate[i] = 1.0 * self.max_derate_factor
                        else:
                            chp_power_derate[i] = 1.0 * self.max_derate_factor - \
                                              self.derate_slope_pct_per_degF * (oa_temp_degF[i] - self.derate_start_temp_degF)
                else:
                    # otherwise, power de-rate of turbocharged engines is not modeled as a function of elevation
                    # add a boolean for turbos (upgrade at elevation or not)
                    for i in range(8760 * self.time_steps_per_hour):
                        if oa_temp_degF[i] <= self.derate_start_temp_degF:
                            chp_power_derate[i] = 1.0 * self.max_derate_factor
                        else:
                            chp_power_derate[i] = 1.0 * self.max_derate_factor - \
                                              self.derate_slope_pct_per_degF * (oa_temp_degF[i] - self.derate_start_temp_degF)
            elif self.prime_mover == 'combustion_turbine':
                # CT derate does not take the form like other prime movers (ie do not use 3 generic params)
                # Be careful of info: cannot share power derate info publicly ....use EPA data instead

                # Average Solar de-rate (from Gregg)
                #p1 = -0.000010167585638
                #p2 = -0.002412376387979
                #p3 = 1.167666148633726
                # Gregg's relationship
                #cf_altitude = 1 - (0.1245 * site_elevation_ft / 3.281 / 1000) + 0.0068*(site_elevation_ft / 3.281 / 1000)**2

                #EPA de-rate (Taurus 70)
                p1 = -0.000013122282921
                p2 = -0.003019828034576
                p3 = 1.218517247421827

                #EPA elevation de-rate (linearly extrapolated past 5000 ft)
                cf_altitude = (-0.00004)*site_elevation_ft + 1

                x = oa_temp_degF
                chp_power_derate = [ cf_altitude*(p1*x[i]**2 + p2*x[i] + p3) for i in range(8760 * self.time_steps_per_hour)]
            elif self.prime_mover == 'fuel_cell':
                # do not know exactly what de-rate as a function of elevation looks like for FC's ......
                self.derate_start_temp_degF = self.derate_start_temp_degF * 1
                self.derate_slope_pct_per_degF = self.derate_slope_pct_per_degF * 1
                self.max_derate_factor = self.max_derate_factor * 1

                for i in range(8760 * self.time_steps_per_hour):
                    if oa_temp_degF[i] <= self.derate_start_temp_degF:
                        chp_power_derate[i] = 1.0 * self.max_derate_factor
                    else:
                        chp_power_derate[i] = 1.0 * self.max_derate_factor - \
                                              self.derate_slope_pct_per_degF * (oa_temp_degF[i] - self.derate_start_temp_degF)
            else:
                chp_power_derate = [1.0 for _ in range(8760 * self.time_steps_per_hour)]

            chp_power_derate = list(chp_power_derate)  # convert var type
        else:
            # no power de-rate considered if "use_default_derate" = False
            chp_power_derate = [1.0 for _ in range(8760 * self.time_steps_per_hour)]
            chp_power_derate = list(chp_power_derate) # convert var type

        return  chp_power_derate

    @property
    def prod_factor(self):
        chp_elec_prod_factor = [1.0 for _ in range(8760 * self.time_steps_per_hour)]
        # Note, we are handling boiler efficiency explicitly so not embedding that into chp thermal prod factor
        chp_thermal_prod_factor = [1.0 for _ in range(8760 * self.time_steps_per_hour)]

        return chp_elec_prod_factor, chp_thermal_prod_factor

    def convert_performance_params(self, oa_temp_degF):
        """
        Convert the performance parameter inputs to coefficients used readily in Xpress
        :return: fuel_burn_slope, fuel_burn_intercept, thermal_prod_slope, thermal_prod_intercept
        """
        fuel_burn_full_load = 1 / self.elec_effic_full_load * 3412.0 / 1.0E6 * 1.0  # [MMBtu/hr/kW]
        fuel_burn_half_load = 1 / self.elec_effic_half_load * 3412.0 / 1.0E6 * 0.5  # [MMBtu/hr/kW]
        fuel_burn_slope_nominal = (fuel_burn_full_load - fuel_burn_half_load) / (1.0 - 0.5)  # [MMBtu/hr/kW]
        fuel_burn_intercept_nominal = fuel_burn_full_load - fuel_burn_slope_nominal * 1.0  # [MMBtu/hr/kW_rated]

        # -----Hot water or steam grade correction factor-----
        # functions of T_water_in and T_water_out or P_steam (need to make inputs for these parameters!!!!)
        t_water_in = 160  # [F]
        t_water_out = 180  # [F]
        if self.prime_mover == 'micro_turbine':

            p00 = 363.9501194987893
            p10 = 2.7767557065540
            p01 = -3.1075752042224
            p20 = -0.0026729333894
            p11 = -0.0039858917853
            p02 = 0.0053427265144

            x = t_water_in
            y = t_water_out
            normalization_factor = 238.751  # [kW_th]
            cf_tp_grade_full_load = (p00 + p10*x + p01*y + p20*x**2 + p11*x*y + p02*y**2) / normalization_factor
            cf_tp_grade_half_load = cf_tp_grade_full_load
        elif self.prime_mover == 'recip_engine':
            cf_tp_grade_full_load = 1
            cf_tp_grade_half_load = 1
        elif self.prime_mover == 'combustion_turbine':
            p_steam = 150 #default
            if p_steam <= 150:
                cf_tp_grade_full_load = 1
            else:
                cf_tp_grade_full_load = 1 - (p_steam - 150)*((1-0.94)/(300-150))
            cf_tp_grade_half_load = cf_tp_grade_full_load
        elif self.prime_mover == 'fuel_cell':
            cf_tp_grade_full_load = 1
            cf_tp_grade_half_load = 1
        else:
            cf_tp_grade_full_load = 1
            cf_tp_grade_half_load = 1

        thermal_prod_full_load = cf_tp_grade_full_load * (1.0 * 1 / self.elec_effic_full_load * self.thermal_effic_full_load * 3412.0 / 1.0E6)  # [MMBtu/hr/kW]
        thermal_prod_half_load = cf_tp_grade_half_load * (0.5 * 1 / self.elec_effic_half_load * self.thermal_effic_half_load * 3412.0 / 1.0E6)  # [MMBtu/hr/kW]
        thermal_prod_slope_nominal = (thermal_prod_full_load - thermal_prod_half_load) / (1.0 - 0.5)  # [MMBtu/hr/kW]
        thermal_prod_intercept_nominal = thermal_prod_full_load - thermal_prod_slope_nominal * 1.0  # [MMBtu/hr/kW_rated]

        # -----Ambient correction factor-----
        # functions of T_amb (shift ISO part load thermal production and fuel burn curves)
        t_amb_f = np.array(oa_temp_degF)
        if self.use_default_derate:
            if self.prime_mover == 'micro_turbine':
                # see thesis
                use_cf = 1 #placeholder boolean
                if use_cf == 0:
                    cf_fb = np.ones(8760 * self.time_steps_per_hour)  # initialize
                    cf_tp = np.ones(8760 * self.time_steps_per_hour)  # initialize
                else:
                    #cf_fb = [0.9529*np.exp(0.0008249*t_amb_f[i]) - (7.496*(10**(-6)))*np.exp(0.06726*t_amb_f[i]) \
                     #    for i in range(8760 * self.time_steps_per_hour)] # this func breaks down after 120 F
                        #fine tuned func (acts linearly past 120 F, cold temp efficiency reduced slightly)
                    cf_fb = [0.0007071*t_amb_f[i] + 0.9587 for i in range(8760 * self.time_steps_per_hour)]
                    cf_tp = [0.005852 * t_amb_f[i] + 0.6615 for i in range(8760 * self.time_steps_per_hour)]
            elif self.prime_mover == 'recip_engine':
                # see thesis (these can change but for sake of generality and lack of sensitivity, it seems best to ...
                # keep these corrections to values of 1)
                cf_fb = np.ones(8760 * self.time_steps_per_hour)
                cf_tp = np.ones(8760 * self.time_steps_per_hour)
            elif self.prime_mover == 'combustion_turbine':
                # see DOE CHP eCatalog (CT's are also sensitive similar to MT's)
                cf_fb = np.ones(8760 * self.time_steps_per_hour)
                cf_tp = np.ones(8760 * self.time_steps_per_hour)
            elif self.prime_mover == 'fuel_cell':
                # do not know how a FC behaves
                cf_fb = np.ones(8760 * self.time_steps_per_hour)
                cf_tp = np.ones(8760 * self.time_steps_per_hour)
            else:
                cf_fb = np.ones(8760 * self.time_steps_per_hour)
                cf_tp = np.ones(8760 * self.time_steps_per_hour)
        else:
            cf_fb = np.ones(8760 * self.time_steps_per_hour)
            cf_tp = np.ones(8760 * self.time_steps_per_hour)


        # FUEL BURN CALCULATIONS
        fuel_burn_slope = [cf_fb[i] * fuel_burn_slope_nominal for i in range(8760 * self.time_steps_per_hour)] # [MMBtu/hr/kW]
        fuel_burn_intercept = [cf_fb[i] * fuel_burn_intercept_nominal for i in range(8760 * self.time_steps_per_hour)] # [MMBtu/hr/kW_rated]
        fuel_burn_slope = list(fuel_burn_slope)  # convert var type
        fuel_burn_intercept = list(fuel_burn_intercept)  # convert var type

        # THERMAL PRODUCTION CALCULATIONS
        thermal_prod_slope = [cf_tp[i] * thermal_prod_slope_nominal for i in range(8760 * self.time_steps_per_hour)] # [MMBtu/hr/kW]
        thermal_prod_intercept = [cf_tp[i] * thermal_prod_intercept_nominal for i in range(8760 * self.time_steps_per_hour)] # [MMBtu/hr/kW_rated]
        thermal_prod_slope = list(thermal_prod_slope)  # convert var type
        thermal_prod_intercept = list(thermal_prod_intercept)  # convert var type

        return fuel_burn_slope, fuel_burn_intercept, thermal_prod_slope, thermal_prod_intercept


class Boiler(Tech):

    boiler_efficiency_defaults = {"hot_water": 0.80,
                                  "steam": 0.75}

    boiler_type_by_chp_prime_mover_defaults = {"recip_engine": "hot_water",
                                               "micro_turbine": "hot_water",
                                               "combustion_turbine": "steam",
                                               "fuel_cell": "hot_water"}

    def __init__(self, dfm, boiler_fuel_series_bau, **kwargs):
        super(Boiler, self).__init__(**kwargs)

        self.loads_served = ['boiler', 'tes']
        self.is_hot = True
        self.reopt_class = 'BOILER'  # Not sure why UTIL tech is not assigned to the UTIL class
        self.min_mmbtu_per_hr = kwargs.get('min_mmbtu_per_hr')
        self.max_mmbtu_per_hr = kwargs.get('max_mmbtu_per_hr')
        self.max_thermal_factor_on_peak_load = kwargs.get('max_thermal_factor_on_peak_load')
        self.existing_boiler_production_type_steam_or_hw = kwargs.get('existing_boiler_production_type_steam_or_hw')
        self.boiler_efficiency = kwargs.get('boiler_efficiency')
        self.installed_cost_us_dollars_per_mmbtu_per_hr = kwargs.get('installed_cost_us_dollars_per_mmbtu_per_hr')
        self.derate = 0
        self.n_timesteps = dfm.n_timesteps

        # Unless max_mmbtu_per_hr is a user-input, set the max_mmbtu_per_hr with the heating load and factor
        if self.max_mmbtu_per_hr is None:
            self.max_mmbtu_per_hr = max(boiler_fuel_series_bau) * self.boiler_efficiency * \
                                    self.max_thermal_factor_on_peak_load

        dfm.add_boiler(self)

    @property
    def prod_factor(self):

        # Note boiler efficiency is explicitly accounted for instead of being embedded in the prod_factor
        boiler_prod_factor = [1.0 for _ in range(self.n_timesteps)]

        return boiler_prod_factor


class ElectricChiller(Tech):

    electric_chiller_cop_defaults = {"convert_elec_to_thermal": 4.55,
                                        "less_than_100_tons": 4.40,
                                        "greater_than_100_tons": 4.69}

    def __init__(self, dfm, chiller_electric_series_bau, **kwargs):
        super(ElectricChiller, self).__init__(**kwargs)

        self.loads_served = ['retail', 'tes']
        self.is_cool = True
        self.reopt_class = 'ELECCHL'
        self.min_kw = kwargs.get('min_kw')
        self.max_kw = kwargs.get('max_kw')
        self.max_thermal_factor_on_peak_load = kwargs.get('max_thermal_factor_on_peak_load')
        self.chiller_cop = kwargs.get('chiller_cop')
        self.installed_cost_us_dollars_per_kw = kwargs.get('installed_cost_us_dollars_per_kw')
        self.derate = 0
        self.n_timesteps = dfm.n_timesteps

        # Update COP (if not user-entered) based on estimated max chiller load
        if self.chiller_cop is None:
            self.max_cooling_load_tons = max(chiller_electric_series_bau) / 3.51685 * \
                                    ElectricChiller.electric_chiller_cop_defaults["convert_elec_to_thermal"]
            self.max_chiller_thermal_capacity_tons = self.max_cooling_load_tons * \
                                                self.max_thermal_factor_on_peak_load
            if self.max_chiller_thermal_capacity_tons < 100.0:
                self.chiller_cop = ElectricChiller.electric_chiller_cop_defaults["less_than_100_tons"]
            else:
                self.chiller_cop = ElectricChiller.electric_chiller_cop_defaults["greater_than_100_tons"]
        else:
            self.max_cooling_load_tons = max(chiller_electric_series_bau) * self.chiller_cop / 3.51685
            self.max_chiller_thermal_capacity_tons = self.max_cooling_load_tons * \
                                                     self.max_thermal_factor_on_peak_load

        # Unless max_kw is a user-input, set the max_kw with the cooling load and factor
        if self.max_kw is None:
            self.max_kw = self.max_chiller_thermal_capacity_tons * 3.51685

        dfm.add_electric_chiller(self)

    @property
    def prod_factor(self):

        # Chiller ProdFactor is where we can account for increased/decreased thermal capacity based on OA temps
        # Note chiller_cop is explicitly accounted for instead of being embedded in the prod_factor
        chiller_prod_factor = [1.0 for _ in range(self.n_timesteps)]

        return chiller_prod_factor


class AbsorptionChiller(Tech):

    absorption_chiller_cop_defaults = {"hot_water": 0.74,
                                       "steam": 1.42}

    # Data format for cost is (ton, $/ton, $/ton/yr); less than 1st or greater than last size uses constant, otherwise lin-interp
    absorption_chiller_cost_defaults = {"hot_water": [(50, 6000.0, 42.0), (440, 2250.0, 14.0), (1320, 2000.0, 7.0)],
                                        "steam": [(330, 3300.0, 21.0), (1000, 2000.0, 7.0)]}

    def __init__(self, dfm, max_cooling_load_tons, hw_or_steam, chp_prime_mover, **kwargs):
        super(AbsorptionChiller, self).__init__(**kwargs)

        self.loads_served = ['retail', 'tes']
        self.is_cool = True
        self.reopt_class = 'ABSORPCHL'
        self.chiller_cop = kwargs.get('chiller_cop')
        self.derate = 0
        self.n_timesteps = dfm.n_timesteps

        # Convert a size-based inputs from ton to kwt
        self.min_kw = kwargs.get('min_ton') * 3.51685
        self.max_kw = kwargs.get('max_ton') * 3.51685
        self.installed_cost_us_dollars_per_ton = kwargs.get('installed_cost_us_dollars_per_ton')
        self.om_cost_us_dollars_per_ton = kwargs.get('om_cost_us_dollars_per_ton')
        self.max_cooling_load_tons = max_cooling_load_tons
        self.hw_or_steam = hw_or_steam
        self.chp_prime_mover = chp_prime_mover

        # Calc default CapEx and OpEx costs, and use if the user did not enter a value
        installed_cost_per_ton_calc, om_cost_per_ton_per_yr_calc = self.get_absorp_chiller_costs(
            self.max_cooling_load_tons, self.hw_or_steam, self.chp_prime_mover)

        if self.installed_cost_us_dollars_per_ton is None and self.om_cost_us_dollars_per_ton is None:
            self.installed_cost_us_dollars_per_ton = installed_cost_per_ton_calc
            self.om_cost_us_dollars_per_ton = om_cost_per_ton_per_yr_calc
        elif self.installed_cost_us_dollars_per_ton is None:
            self.installed_cost_us_dollars_per_ton = installed_cost_per_ton_calc
        elif self.om_cost_us_dollars_per_ton is None:
            self.om_cost_us_dollars_per_ton = om_cost_per_ton_per_yr_calc

        self.installed_cost_us_dollars_per_kw = self.installed_cost_us_dollars_per_ton / 3.51685
        self.om_cost_us_dollars_per_kw = self.om_cost_us_dollars_per_ton / 3.51685

        self.incentives = IncentivesNoProdBased(**kwargs)

        dfm.add_absorption_chiller(self)

    @property
    def prod_factor(self):

        # Chiller ProdFactor is where we can account for increased/decreased thermal capacity based on OA temps
        # Note chiller_cop is explicitly accounted for instead of being embedded in the prod_factor
        chiller_prod_factor = [1.0 for _ in range(self.n_timesteps)]

        return chiller_prod_factor

    @staticmethod
    def get_absorp_chiller_costs(max_cooling_load_tons, hw_or_steam, chp_prime_mover):
        if hw_or_steam is not None:
            defaults_sizes = AbsorptionChiller.absorption_chiller_cost_defaults[hw_or_steam]
        elif chp_prime_mover is not None:
            defaults_sizes = AbsorptionChiller.absorption_chiller_cost_defaults[Boiler.boiler_type_by_chp_prime_mover_defaults[chp_prime_mover]]
        else:
            # If hw_or_steam and CHP prime_mover are not provided, use hot_water defaults
            defaults_sizes = AbsorptionChiller.absorption_chiller_cost_defaults["hot_water"]

        if max_cooling_load_tons <= defaults_sizes[0][0]:
            absorp_chiller_capex = defaults_sizes[0][1]
            absorp_chiller_opex = defaults_sizes[0][2]
        elif max_cooling_load_tons >= defaults_sizes[-1][0]:
            absorp_chiller_capex = defaults_sizes[-1][1]
            absorp_chiller_opex = defaults_sizes[-1][2]
        else:
            for size in range(1, len(defaults_sizes)):
                if max_cooling_load_tons > defaults_sizes[size - 1][0] and \
                        max_cooling_load_tons <= defaults_sizes[size][0]:
                    slope_capex = (defaults_sizes[size][1] - defaults_sizes[size - 1][1]) / \
                                  (defaults_sizes[size][0] - defaults_sizes[size - 1][0])
                    slope_opex = (defaults_sizes[size][2] - defaults_sizes[size - 1][2]) / \
                                 (defaults_sizes[size][0] - defaults_sizes[size - 1][0])
                    absorp_chiller_capex = defaults_sizes[size - 1][1] + slope_capex * \
                                           (max_cooling_load_tons - defaults_sizes[size - 1][0])
                    absorp_chiller_opex = defaults_sizes[size - 1][2] + slope_opex * \
                                          (max_cooling_load_tons - defaults_sizes[size - 1][0])

        return absorp_chiller_capex, absorp_chiller_opex

