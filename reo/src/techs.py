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
                 fuel_avail_before_outage_pct=1, **kwargs):
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
    useable for Xpress (e.g. fuel burn rate in MMBtu/hr/kW_rated (y-intercept)

    """

    def __init__(self, dfm, run_uuid, existing_boiler_production_type_steam_or_hw, oa_temp_degF, site_elevation_ft,
                 time_steps_per_hour=1, **kwargs):
        super(CHP, self).__init__()

        self.prime_mover = kwargs.get('prime_mover')
        self.existing_boiler_production_type_steam_or_hw = existing_boiler_production_type_steam_or_hw
        self.reopt_class = 'CHP'
        self.is_chp = True
        self.time_steps_per_hour = time_steps_per_hour
        self.derate = 1  # Need to rectify this legacy derate, maybe remove this and replace if no needed (NM/IL?)
        self.loads_served = ['retail', 'wholesale', 'export', 'storage', 'boiler', 'tes']
        self.incentives = Incentives(**kwargs)

        try:
            self.min_kw = kwargs['min_kw']
            self.max_kw = kwargs['max_kw']
            self.installed_cost_us_dollars_per_kw = kwargs['installed_cost_us_dollars_per_kw']
            self.om_cost_us_dollars_per_kw = kwargs['om_cost_us_dollars_per_kw']
            self.om_cost_us_dollars_per_kwh = kwargs['om_cost_us_dollars_per_kwh']
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
        except:
            print("Prime mover type was not specified and not all cost/performance parameters were input "
                  "in the post")

        self.fuel_burn_slope, self.fuel_burn_intercept, self.thermal_prod_slope, self.thermal_prod_intercept = \
            self.convert_performance_params(self.elec_effic_full_load, self.elec_effic_half_load,
                                            self.thermal_effic_full_load,
                                            self.thermal_effic_half_load)
        if self.use_default_derate:
            # TODO: Use either site altitude OR derate_max, depending on which, if any, are input. VALIDATORS.PY to handle this!
            # TODO: implement derate factor array based on input temperature profile, with derate_max from above TODO
            self.chp_power_derate = [1.0 for _ in range(8760 * self.time_steps_per_hour)]

        dfm.add_chp(self)

    @property
    def prod_factor(self):
        chp_elec_prod_factor = [1.0 for _ in range(8760 * self.time_steps_per_hour)]
        # Note, we are handling boiler efficiency explicitly so not embedding that into chp thermal prod factor
        chp_thermal_prod_factor = [1.0 for _ in range(8760 * self.time_steps_per_hour)]

        return chp_elec_prod_factor, chp_thermal_prod_factor

    @staticmethod
    def convert_performance_params(elec_effic_full_load, elec_effic_half_load, thermal_effic_full_load,
                                   thermal_effic_half_load):
        """
        Convert the performance parameter inputs to coefficients used readily in Xpress
        :return: fuel_burn_slope, fuel_burn_intercept, thermal_prod_slope, thermal_prod_intercept
        """

        fuel_burn_full_load = 1 / elec_effic_full_load * 3412.0 / 1.0E6 * 1.0  # [MMBtu/hr/kW]
        fuel_burn_half_load = 1 / elec_effic_half_load * 3412.0 / 1.0E6 * 0.5  # [MMBtu/hr/kW]
        fuel_burn_slope = (fuel_burn_full_load - fuel_burn_half_load) / (1.0 - 0.5)  # [MMBtu/hr/kW]
        fuel_burn_intercept = fuel_burn_full_load - fuel_burn_slope * 1.0  # [MMBtu/hr/kW_rated]

        thermal_prod_full_load = 1.0 * 1 / elec_effic_full_load * \
                                 thermal_effic_full_load * 3412.0 / 1.0E6  # [MMBtu/hr/kW]
        thermal_prod_half_load = 0.5 * 1 / elec_effic_half_load * \
                                 thermal_effic_half_load * 3412.0 / 1.0E6   # [MMBtu/hr/kW]
        thermal_prod_slope = (thermal_prod_full_load - thermal_prod_half_load) / (1.0 - 0.5)  # [MMBtu/hr/kW]
        thermal_prod_intercept = thermal_prod_full_load - thermal_prod_slope * 1.0  # [MMBtu/hr/kW_rated]


        return fuel_burn_slope, fuel_burn_intercept, thermal_prod_slope, thermal_prod_intercept


class Boiler(Tech):

    boiler_efficiency_defaults = {"hot_water": 0.80,
                                  "steam": 0.75}

    def __init__(self, dfm, min_mmbtu_per_hr, max_mmbtu_per_hr, existing_boiler_production_type_steam_or_hw,
                 boiler_efficiency, installed_cost_us_dollars_per_mmbtu_per_hr, **kwargs):
        super(Boiler, self).__init__(**kwargs)

        self.loads_served = ['boiler', 'tes']  # Not sure if boiler would ever store thermal in tes if no TOU for NG
        self.is_hot = True
        self.reopt_class = 'BOILER'  # Not sure why UTIL tech is not assigned to the UTIL class
        self.min_mmbtu_per_hr = min_mmbtu_per_hr
        self.max_mmbtu_per_hr = max_mmbtu_per_hr
        self.existing_boiler_production_type_steam_or_hw = existing_boiler_production_type_steam_or_hw
        self.boiler_efficiency = boiler_efficiency
        self.installed_cost_us_dollars_per_mmbtu_per_hr = installed_cost_us_dollars_per_mmbtu_per_hr
        self.derate = 0
        self.n_timesteps = dfm.n_timesteps

        dfm.add_boiler(self)

    @property
    def prod_factor(self):

        # Note boiler efficiency is explicitly accounted for instead of being embedded in the prod_factor
        boiler_prod_factor = [1.0 for _ in range(self.n_timesteps)]

        return boiler_prod_factor


class ElectricChiller(Tech):

    def __init__(self, dfm, min_kw, max_kw, chiller_cop, installed_cost_us_dollars_per_kw, **kwargs):
        super(ElectricChiller, self).__init__(**kwargs)

        self.loads_served = ['retail', 'tes']
        self.is_cool = True
        self.reopt_class = 'ELECCHL'
        self.min_kw = min_kw
        self.max_kw = max_kw
        self.chiller_cop = chiller_cop
        self.installed_cost_us_dollars_per_kw = installed_cost_us_dollars_per_kw
        self.derate = 0
        self.n_timesteps = dfm.n_timesteps

        dfm.add_electric_chiller(self)

    @property
    def prod_factor(self):

        # Chiller ProdFactor is where we can account for increased/decreased thermal capacity based on OA temps
        # Note chiller_cop is explicitly accounted for instead of being embedded in the prod_factor
        chiller_prod_factor = [1.0 for _ in range(self.n_timesteps)]

        return chiller_prod_factor


class AbsorptionChiller(Tech):

    def __init__(self, dfm, chiller_cop, min_ton, max_ton, installed_cost_us_dollars_per_ton,
                 om_cost_us_dollars_per_ton, **kwargs):
        super(AbsorptionChiller, self).__init__(**kwargs)

        self.loads_served = ['retail', 'tes']
        self.is_cool = True
        self.reopt_class = 'ABSORPCHL'
        self.chiller_cop = chiller_cop
        self.derate = 0
        self.n_timesteps = dfm.n_timesteps

        # Convert a size-based inputs from ton to kwt
        self.min_kw = min_ton * 3.51685
        self.max_kw = max_ton * 3.51685
        self.installed_cost_us_dollars_per_kw = installed_cost_us_dollars_per_ton / 3.51685
        self.om_cost_us_dollars_per_kw = om_cost_us_dollars_per_ton / 3.51685

        self.incentives = IncentivesNoProdBased(**kwargs)

        dfm.add_absorption_chiller(self)

    @property
    def prod_factor(self):

        # Chiller ProdFactor is where we can account for increased/decreased thermal capacity based on OA temps
        # Note chiller_cop is explicitly accounted for instead of being embedded in the prod_factor
        chiller_prod_factor = [1.0 for _ in range(self.n_timesteps)]

        return chiller_prod_factor

