from sscapi import PySSC

class WindSAMSDK:

    wind_turbine_speeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
    large_wind_turbine_powercurve = [0, 0, 0, 52.589248657226563, 124.65599822998047, 243.46875,  420.7139892578125,
                                     668.0782470703125, 997.24798583984375, 1419.9097900390625, 1500, 1500, 1500, 1500,
                                     1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]
    large_rotor_diameter = 53.5
    large_system_capacity = 1500

    def __init__(self,
                 latitude=None,
                 longitude=None,
                 elevation=None,
                 year=None,
                 size_class='commercial',
                 temperatures_celcius=None,
                 pressures_atmospheres=None,
                 hub_height_meters=None,
                 wind_direction_degrees=None,
                 wind_meters_per_sec=None):

        self.elevation = elevation
        self.latitude=latitude
        self.longitude=longitude
        self.year = year
        self.size_class = size_class
        self.hub_height_meters = hub_height_meters

        self.temperatures_celcius = temperatures_celcius
        self.pressure_atmospheres = pressures_atmospheres
        self.wind_direction_degrees = wind_direction_degrees
        self.wind_meters_per_sec = wind_meters_per_sec

        self.ssc = []
        self.data = []
        self.module = []


    def make_ssc(self):

        ssc = PySSC()
        ssc.module_exec_set_print(0)
        data = ssc.data_create()
        module = ssc.module_create('windpower')


        turbine_powercurve = None
        rotor_diameter = None
        system_capacity = None

        if self.size_class == 'commercial':
            #commercial turbine
        elif self.size_class == 'midsize':
            #midsize
        elif self.size_class == 'large':
            turbine_powercurve = self.large_wind_turbine_powercurve
            rotor_diameter = self.large_rotor_diameter
            system_capacity = self.large_rotor_diameter


        wind_data = dict()
        wind_data['latitude'] = self.latitude
        wind_data['longitude'] = self.longitude
        wind_data['elevation'] = self.elevation
        wind_data['year'] = self.year
        wind_data['heights'] = [self.hub_height_meters, self.hub_height_meters, self.hub_height_meters, self.hub_height_meters]
        wind_data['fields'] [1, 2, 3, 4]
        wind_data['data'] = [self.temperatures_celcius, self.pressure_atmospheres, self.wind_direction_degrees, self.wind_meters_per_sec]

        ssc.data_set_table(data, 'wind_resource_data', wind_data)
        ssc.data_set_number(data, 'wind_resource_shear', 0.14000000059604645)
        ssc.data_set_number(data, 'wind_resource_turbulence_coeff', 0.10000000149011612)
        ssc.data_set_number(data, 'system_capacity', system_capacity)
        ssc.data_set_number(data, 'wind_resource_model_choice', 0)
        ssc.data_set_number(data, 'weibull_reference_height', 50)
        ssc.data_set_number(data, 'weibull_k_factor', 2)
        ssc.data_set_number(data, 'weibull_wind_speed', 7.25)
        ssc.data_set_number(data, 'wind_turbine_rotor_diameter', rotor_diameter)
        ssc.data_set_array(data, 'wind_turbine_powercurve_windspeeds', self.wind_turbine_speeds)
        ssc.data_set_array(data, 'wind_turbine_powercurve_powerout', turbine_powercurve);
        ssc.data_set_number(data, 'wind_turbine_hub_ht', 80)
        ssc.data_set_number(data, 'wind_turbine_max_cp', 0.44999998807907104)
        wind_farm_xCoordinates = [0];
        ssc.data_set_array(data, 'wind_farm_xCoordinates', wind_farm_xCoordinates);
        wind_farm_yCoordinates = [0];
        ssc.data_set_array(data, 'wind_farm_yCoordinates', wind_farm_yCoordinates);
        ssc.data_set_number(data, 'wind_farm_losses_percent', 0)
        ssc.data_set_number(data, 'wind_farm_wake_model', 0)
        ssc.data_set_number(data, 'adjust:constant', 0)

        if ssc.module_exec(module, data) == 0:
            print ('windpower simulation error')
            idx = 1
            msg = ssc.module_log(module, 0)
            while (msg != None):
                print ('	: ' + msg)
                msg = ssc.module_log(module, idx)
                idx = idx + 1
        ssc.module_free(module)
        annual_energy = ssc.data_get_number(data, 'annual_energy');
        print 'Annual energy (year 1) = ', annual_energy
        capacity_factor = ssc.data_get_number(data, 'capacity_factor');
        print 'Capacity factor (year 1) = ', capacity_factor
        ssc.data_free(data);

