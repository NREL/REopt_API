from sscapi import PySSC
import numpy as np
from reo.log_levels import log
from exceptions import RuntimeError

class WindSAMSDK:

    rotor_diameter = dict()
    wind_turbine_powercurve = dict()
    system_capacity = dict()
    wind_turbine_speeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

    def __init__(self,
                 hub_height_meters=None,
                 latitude=None,
                 longitude=None,
                 elevation=0,  # not actually used in SDK
                 year=2012,    # not used in SDK, but required
                 size_class='commercial',
                 temperature_celsius=None,
                 pressure_atmospheres=None,
                 wind_meters_per_sec=None,
                 wind_direction_degrees=None,
                 **kwargs
                 ):

        self.elevation = elevation
        self.latitude=latitude
        self.longitude=longitude
        self.year = year
        self.size_class = size_class
        self.hub_height_meters = hub_height_meters

        if temperature_celsius is None or pressure_atmospheres is \
                None or wind_direction_degrees is None or wind_meters_per_sec is None:

            from reo.src.wind_resource import get_wind_resource
            try:
                wind_data = get_wind_resource(
                    latitude=self.latitude,
                    longitude=self.longitude,
                    hub_height_meters=self.hub_height_meters,
                    time_steps_per_hour=1
                )
                self.temperature_celsius = wind_data['temperature_celsius']
                self.pressure_atmospheres = wind_data['pressure_atmospheres']
                self.wind_meters_per_sec = wind_data['wind_meters_per_sec']
                self.wind_direction_degrees = wind_data['wind_direction_degrees']
            except ValueError as e:
               log.error("Latitude/longitude is outside of wind resource dataset bounds.")
            except:
                log.error("Wind data download timed out")
                raise RuntimeError("Wind data download timed out")
        else:
            self.temperature_celsius = temperature_celsius
            self.pressure_atmospheres = pressure_atmospheres
            self.wind_direction_degrees = wind_direction_degrees
            self.wind_meters_per_sec = wind_meters_per_sec

        self.wind_turbine_powercurve['large'] = [0, 0, 0, 70.119, 166.208, 324.625, 560.952, 890.771, 1329.664,
                                                 1893.213, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000,
                                                 2000, 2000, 2000, 2000, 2000, 2000]

        self.wind_turbine_powercurve['medium'] = [0, 0, 0, 8.764875, 20.776, 40.578125, 70.119, 111.346375, 166.208,
                                                  236.651625, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250,
                                                  250, 250, 250, 250, 250]

        self.wind_turbine_powercurve['commercial'] = [0, 0, 0, 3.50595, 8.3104, 16.23125, 28.0476, 44.53855, 66.4832,
                                                      94.66065, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
                                                      100, 100, 100, 100, 100]

        self.wind_turbine_powercurve['residential'] = [0, 0, 0, 0.070542773, 0.1672125, 0.326586914, 0.564342188,
                                                       0.896154492, 1.3377, 1.904654883, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                                                       2.5, 2.5, 2.5, 0, 0, 0, 0, 0, 0, 0]

        self.rotor_diameter['large'] = 55
        self.rotor_diameter['medium'] = 21.9
        self.rotor_diameter['commercial'] = 13.8
        self.rotor_diameter['residential'] = 1.85

        self.system_capacity['large'] = 2000
        self.system_capacity['medium'] = 250
        self.system_capacity['commercial'] = 100
        self.system_capacity['residential'] = 2.5


        self.ssc = []
        self.data = []
        self.module = []

        self.make_ssc()

    def make_ssc(self):

        ssc = PySSC()
        ssc.module_exec_set_print(0)
        data = ssc.data_create()
        module = ssc.module_create('windpower')

        # must setup wind resource in it's own ssc data structure
        wind_resource = ssc.data_create()

        ssc.data_set_number(wind_resource, 'latitude', self.latitude)
        ssc.data_set_number(wind_resource, 'longitude', self.longitude)
        ssc.data_set_number(wind_resource, 'elevation', self.elevation)
        ssc.data_set_number(wind_resource, 'year', self.year)
        heights = [self.hub_height_meters, self.hub_height_meters, self.hub_height_meters, self.hub_height_meters]
        ssc.data_set_array(wind_resource, 'heights', heights)
        fields = [1, 2, 3, 4]
        ssc.data_set_array(wind_resource, 'fields', fields)
        data_matrix = np.matrix([self.temperature_celsius, self.pressure_atmospheres, self.wind_meters_per_sec, self.wind_direction_degrees])
        data_matrix = data_matrix.transpose()
        ssc.data_set_matrix(wind_resource, 'data', data_matrix.tolist() )

        ssc.data_set_table(data, 'wind_resource_data', wind_resource)
        ssc.data_set_number(data, 'wind_resource_shear', 0.14000000059604645)
        ssc.data_set_number(data, 'wind_resource_turbulence_coeff', 0.10000000149011612)
        ssc.data_set_number(data, 'system_capacity', self.system_capacity[self.size_class])
        ssc.data_set_number(data, 'wind_resource_model_choice', 0)
        ssc.data_set_number(data, 'weibull_reference_height', 50)
        ssc.data_set_number(data, 'weibull_k_factor', 2)
        ssc.data_set_number(data, 'weibull_wind_speed', 7.25)
        ssc.data_set_number(data, 'wind_turbine_rotor_diameter', self.rotor_diameter[self.size_class])
        ssc.data_set_array(data, 'wind_turbine_powercurve_windspeeds', self.wind_turbine_speeds)
        ssc.data_set_array(data, 'wind_turbine_powercurve_powerout', self.wind_turbine_powercurve[self.size_class]);
        ssc.data_set_number(data, 'wind_turbine_hub_ht', 80)
        ssc.data_set_number(data, 'wind_turbine_max_cp', 0.44999998807907104)
        wind_farm_xCoordinates = [0]
        ssc.data_set_array(data, 'wind_farm_xCoordinates', wind_farm_xCoordinates)
        wind_farm_yCoordinates = [0]
        ssc.data_set_array(data, 'wind_farm_yCoordinates', wind_farm_yCoordinates)
        ssc.data_set_number(data, 'wind_farm_losses_percent', 0)
        ssc.data_set_number(data, 'wind_farm_wake_model', 0)
        ssc.data_set_number(data, 'adjust:constant', 0)

        ssc.data_free(wind_resource)
        self.ssc = ssc
        self.data = data
        self.module = module

    def wind_prod_factor(self):

        if self.ssc.module_exec(self.module, self.data) == 0:
            print ('windpower simulation error')
            idx = 1
            msg = self.ssc.module_log(self.module, 0)
            while (msg != None):
                print ('	: ' + msg)
                msg = self.ssc.module_log(self.module, idx)
                idx = idx + 1
        self.ssc.module_free(self.module)
        system_power = self.ssc.data_get_array(self.data, 'gen')
        prod_factor = [power/self.system_capacity[self.size_class] for power in system_power]
        self.ssc.data_free(self.data)
        return prod_factor



