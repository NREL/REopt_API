from reo.src.dat_file_manager import big_number
from reo.src.pvwatts import PVWatts
from reo.src.wind import WindSAMSDK
from reo.src.incentives import Incentives
from reo.src.ventyx import Ventyx
from reo.models import GeneratorModel

class Tech(object):
    """
    base class for REopt energy generation technology
    """

    def __init__(self, min_kw=0, max_kw=big_number, installed_cost_us_dollars_per_kw=big_number,
                 om_cost_us_dollars_per_kw=0, *args, **kwargs):

        self.min_kw = min_kw
        self.max_kw = max_kw
        self.installed_cost_us_dollars_per_kw = installed_cost_us_dollars_per_kw
        self.om_cost_us_dollars_per_kw = om_cost_us_dollars_per_kw

        self.loads_served = ['retail', 'wholesale', 'export', 'storage']
        self.nmil_regime = None
        self.reopt_class = ""
        self.is_grid = False
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
        self.is_grid = True
        self.derate = 0
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
        0: 0, # ground-mount fixed array type's tilt should be equal to the latitude
        1: 10,
        2: 0,
        3: 0,
        4:0
    }

    def __init__(self, dfm, degradation_pct, time_steps_per_hour=1, acres_per_kw=6e-3, kw_per_square_foot=0.01, existing_kw=0, **kwargs):
        super(PV, self).__init__(**kwargs)

        self.degradation_pct = degradation_pct
        self.nmil_regime = 'BelowNM'
        self.reopt_class = 'PV'
        self.acres_per_kw = acres_per_kw
        self.kw_per_square_foot = kw_per_square_foot
        self.time_steps_per_hour = time_steps_per_hour
        self.incentives = Incentives(**kwargs)
        self.tilt = kwargs['tilt']

        self.pvwatts_prod_factor = None
        self.existing_kw = existing_kw
        self.min_kw += existing_kw

        # if user hasn't entered the tilt, tilt value gets assigned based on array_type
        if self.tilt == 0.537:
            if kwargs.get('array_type') == 0:
                self.tilt = kwargs.get('latitude')
            else:
                self.tilt = PV.array_type_to_tilt_angle[kwargs.get('array_type')]
        self.kwargs['tilt']  = self.tilt

        # if user has entered the max_kw for new PV to be less than the user-specified existing_pv, max_kw is reset
        if self.max_kw < self.existing_kw:
            self.max_kw = self.existing_kw

        self.pvwatts = PVWatts(time_steps_per_hour=self.time_steps_per_hour, **self.kwargs)

        dfm.add_pv(self)

    @property
    def prod_factor(self):

        if self.pvwatts_prod_factor is None:
            self.pvwatts_prod_factor = self.pvwatts.pv_prod_factor
        return self.pvwatts_prod_factor

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
        'residential': 10792,
        'commercial': 4989,
        'medium': 4111,
        'large': 1874,
    }

    size_class_to_itc_incentives = {
        'residential': 0.3,
        'commercial': 0.3,
        'medium': 0.12,
        'large': 0.12,
    }

    def __init__(self, dfm, acres_per_kw=.03,time_steps_per_hour=1, **kwargs):
        super(Wind, self).__init__(**kwargs)

        self.path_inputs = dfm.get_paths()['inputs']
        self.nmil_regime = 'BelowNM'
        self.reopt_class = 'WIND'
        self.acres_per_kw = acres_per_kw
        self.hub_height_meters = Wind.size_class_to_hub_height[kwargs['size_class']]
        self.time_steps_per_hour = time_steps_per_hour
        self.incentives = Incentives(**kwargs)
        self.installed_cost_us_dollars_per_kw = kwargs.get('installed_cost_us_dollars_per_kw')

        # if user hasn't entered the federal itc, itc value gets assigned based on size_class
        if self.incentives.federal.itc == 0.3:
            self.incentives.federal.itc = Wind.size_class_to_itc_incentives[kwargs.get('size_class')]

        # if user hasn't entered the installed cost per kw, it gets assigned based on size_class
        if kwargs.get('installed_cost_us_dollars_per_kw') == 3013:
                self.installed_cost_us_dollars_per_kw = Wind.size_class_to_installed_cost[kwargs.get('size_class')]

        self.ventyx = None
        self.sam_prod_factor = None
        dfm.add_wind(self)

        """
        # restricting max_kw based on size_class constraints reo to consider just 1 turbine per simulation.
        # residential <= 2.5 kW
        # commercial <= 100  kW
        # medium <= 1000 kW
        # Large <= 2500 kW (2.5 MW)

        if kwargs.get('size_class') == 'residential':
            self.max_kw = 2.5
        elif kwargs.get('size_class') == 'commercial':
            self.max_kw = 100
        elif kwargs.get('size_class') == 'medium':
            self.max_kw = 250
        elif kwargs.get('size_class') == 'large':
            self.max_kw = 1000

        if self.min_kw > self.max_kw:
            self.min_kw = self.max_kw
        """

    @property
    def prod_factor(self):
        """
        Pass resource_meters_per_sec to SAM SDK to get production factor
        :return: wind turbine production factor for 1kW system for 1 year with length = 8760 * time_steps_per_hour
        """
        if self.sam_prod_factor is None:
            
            sam = WindSAMSDK(path_inputs=self.path_inputs, hub_height_meters=self.hub_height_meters,
                             time_steps_per_hour=self.time_steps_per_hour, **self.kwargs)
            self.sam_prod_factor = sam.wind_prod_factor()

        # below "prod factor" was tested in desktop to validate API with wind, perhaps integrate into a test
        if self.ventyx is None:
            self.ventyx = Ventyx()
        # return self.ventyx.wind_prod_factor
        return self.sam_prod_factor


class Generator(Tech):

    def __init__(self, dfm, run_uuid, min_kw, max_kw, existing_kw, fuel_slope_gal_per_kwh, fuel_intercept_gal_per_hr, fuel_avail_gal, min_turn_down_pct,
                 outage_start_hour=None, outage_end_hour=None, **kwargs):
        super(Generator, self).__init__(min_kw=min_kw, max_kw=max_kw, **kwargs)
        """
        super class init for generator is not unique anymore as we are now allowing users to define min/max sizes;
        and include diesel generator's size as optimization decision variable.
        
        For assigning the default_slope and default_intercept, the size_kw is being replaced by min_kw.
        """

        self.fuel_slope = fuel_slope_gal_per_kwh
        self.fuel_intercept = fuel_intercept_gal_per_hr
        self.fuel_avail = fuel_avail_gal
        self.min_turn_down = min_turn_down_pct
        self.reopt_class = 'GENERATOR'
        self.outage_start_hour = outage_start_hour
        self.outage_end_hour = outage_end_hour
        self.derate = 0
        self.loads_served = ['retail', 'storage']
        self.min_kw = min_kw
        self.max_kw = max_kw
        self.existing_kw = existing_kw
        self.min_kw += self.existing_kw

        # if user has entered the max_kw for new gen to be less than the user-specified exiting_gen, max_kw is reset
        # in this case existing_kw = max_kw = min_kw, fixing the gen-size decision variable as a constant
        if self.max_kw < self.existing_kw:
            self.max_kw = self.existing_kw

        # no net-metering for gen so it can only sell in "wholesale" bin (and not "export" bin)
        if kwargs['generator_sells_energy_back_to_grid']:
            self.loads_served.append('wholesale')


        default_slope, default_intercept = self.default_fuel_burn_rate(self.min_kw)
        if self.fuel_slope == 0:  # default is zero
            self.fuel_slope = default_slope
            GeneratorModel.objects.filter(run_uuid=run_uuid).update(fuel_slope_gal_per_kwh=self.fuel_slope)
        if self.fuel_intercept == 0:
            self.fuel_intercept = default_intercept
            GeneratorModel.objects.filter(run_uuid=run_uuid).update(fuel_intercept_gal_per_hr=self.fuel_intercept)

        dfm.add_generator(self)

    @property
    def prod_factor(self):
        gen_prod_factor = [0.0 for _ in range(8760)]

        if self.outage_start_hour is not None and self.outage_end_hour is not None:  # generator only available during outage
            gen_prod_factor[self.outage_start_hour:self.outage_end_hour] = [1]*(self.outage_end_hour - self.outage_start_hour)

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
