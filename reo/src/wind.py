import csv
import numpy as np
import os

from sscapi import PySSC

wind_turbine_powercurve_lookup = {'large':[0, 0, 0, 70.119, 166.208, 324.625, 560.952, 890.771, 1329.664,
                                                 1893.213, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000,
                                                 2000, 2000, 2000, 2000, 2000, 2000],
        'medium':[0, 0, 0, 8.764875, 20.776, 40.578125, 70.119, 111.346375, 166.208,
                                                  236.651625, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250,
                                                  250, 250, 250, 250, 250],
        'commercial': [0, 0, 0, 3.50595, 8.3104, 16.23125, 28.0476, 44.53855, 66.4832,
                                                      94.66065, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
                                                      100, 100, 100, 100, 100],
        'residential' :[0, 0, 0, 0.070542773, 0.1672125, 0.326586914, 0.564342188,
                                                       0.896154492, 1.3377, 1.904654883, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                                                       2.5, 2.5, 2.5, 0, 0, 0, 0, 0, 0, 0]}

system_capacity_lookup = {'large': 2000,
        'medium': 250,
        'commercial': 100,
        'residential': 2.5}
       
rotor_diameter_lookup = {'large': 55,
        'medium': 21.9,
        'commercial': 13.8,
        'residential': 1.85}


time_step_hour_to_minute_interval_lookup = {
    round(float(1), 2): '60',
    round(float(0.5),2): '30',
    round(float(0.25),2): '15',
    round(float(5/60),2): '5',
    round(float(1/60),2): '1'}

allowed_hub_height_meters = [10, 40, 60, 80, 100, 120, 140, 160, 200]

class WindSAMSDK:

    wind_turbine_speeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

    def __init__(self,
                 path_inputs=None,
                 hub_height_meters=None,
                 latitude=None,
                 longitude=None,
                 elevation=0,  # not actually used in SDK
                 year=2012,
                 size_class='commercial',
                 temperature_celsius=None,
                 pressure_atmospheres=None,
                 wind_meters_per_sec=None,
                 wind_direction_degrees=None,
                 time_steps_per_hour=1,
                 **kwargs
                 ):

        self.elevation = elevation
        self.latitude = latitude
        self.longitude = longitude
        self.year = year
        self.size_class = size_class
        self.hub_height_meters = hub_height_meters
        self.time_steps_per_hour = time_steps_per_hour
        self.interval = time_step_hour_to_minute_interval_lookup[round(float(time_steps_per_hour), 2)]

        # evaluate hub height, determine what heights to download
        heights = [hub_height_meters]
        if hub_height_meters not in allowed_hub_height_meters:
            height_low = allowed_hub_height_meters[0]
            height_high = allowed_hub_height_meters[-1]
            for h in allowed_hub_height_meters:
                if h < hub_height_meters:
                    height_low = h
                elif h > hub_height_meters:
                    height_high = h
            heights[0] = height_low
            heights.append(height_high)

        file_resource_base = os.path.join(path_inputs, str(latitude) + "_" + str(longitude) + "_windtoolkit_" + str(year) + "_" + str(self.interval) + "min")
        file_resource_full = file_resource_base
        file_resource_heights = {}

        for h in heights:
            file_resource_heights[h] = file_resource_base + '_' + str(h) + 'm.srw'
            file_resource_full += "_" + str(h) + 'm'
        file_resource_full += ".srw"

        self.file_resource_heights = file_resource_heights
        self.file_resource_full = file_resource_full
        self.file_downloaded = os.path.isfile(self.file_resource_full)
        self.use_input_data = False

        # maintain capability to pass in test data directly
        if not None in [temperature_celsius, pressure_atmospheres, wind_direction_degrees, wind_meters_per_sec]:
            self.temperature_celsius = temperature_celsius
            self.pressure_atmospheres = pressure_atmospheres
            self.wind_direction_degrees = wind_direction_degrees
            self.wind_meters_per_sec = wind_meters_per_sec
            self.use_input_data = True

        elif not self.file_downloaded:
            from reo.src.wind_resource import get_wind_resource_developer_api
            
            # currently only available for hourly data
            for height, f in self.file_resource_heights.iteritems():
                success = get_wind_resource_developer_api(
                    filename=f,
                    year=self.year,
                    latitude=self.latitude,
                    longitude=self.longitude,
                    hub_height_meters=height)
                if not success:
                    raise ValueError('Unable to download wind data')

            # combine into one file to pass to SAM
            if len(heights) > 1:
                self.file_downloaded = self.combine_files(self.file_resource_heights, self.file_resource_full)



        self.wind_turbine_powercurve = wind_turbine_powercurve_lookup[size_class] 
        self.system_capacity = system_capacity_lookup[size_class] 
        self.rotor_diameter = rotor_diameter_lookup[size_class] 

        self.ssc = []
        self.data = []
        self.module = []
        self.wind_resource = []
        self.make_ssc()

    def make_ssc(self):

        ssc = PySSC()
        ssc.module_exec_set_print(0)
        data = ssc.data_create()
        module = ssc.module_create('windpower')

        # must setup wind resource in its own ssc data structure
        wind_resource = []
        if self.use_input_data:
            wind_resource = ssc.data_create()

            ssc.data_set_number(wind_resource, 'latitude', self.latitude)
            ssc.data_set_number(wind_resource, 'longitude', self.longitude)
            ssc.data_set_number(wind_resource, 'elevation', self.elevation)
            ssc.data_set_number(wind_resource, 'year', self.year)
            heights = [self.hub_height_meters, self.hub_height_meters, self.hub_height_meters,
                                self.hub_height_meters]
            ssc.data_set_array(wind_resource, 'heights', heights)
            fields = [1, 2, 3, 4]
            ssc.data_set_array(wind_resource, 'fields', fields)
            data_matrix = np.matrix([self.temperature_celsius, self.pressure_atmospheres, self.wind_meters_per_sec,
                                              self.wind_direction_degrees])
            data_matrix = data_matrix.transpose()
            data_matrix = data_matrix.tolist()
            ssc.data_set_matrix(wind_resource, 'data', data_matrix)

            ssc.data_set_table(data, 'wind_resource_data', wind_resource)
        else:
            ssc.data_set_string(data, 'wind_resource_filename', self.file_resource)

        ssc.data_set_number(data, 'wind_resource_shear', 0.14000000059604645)
        ssc.data_set_number(data, 'wind_resource_turbulence_coeff', 0.10000000149011612)
        ssc.data_set_number(data, 'system_capacity', self.system_capacity)
        ssc.data_set_number(data, 'wind_resource_model_choice', 0)
        ssc.data_set_number(data, 'weibull_reference_height', 50)
        ssc.data_set_number(data, 'weibull_k_factor', 2)
        ssc.data_set_number(data, 'weibull_wind_speed', 7.25)
        ssc.data_set_number(data, 'wind_turbine_rotor_diameter', self.rotor_diameter)
        ssc.data_set_array(data, 'wind_turbine_powercurve_windspeeds', self.wind_turbine_speeds)
        ssc.data_set_array(data, 'wind_turbine_powercurve_powerout', self.wind_turbine_powercurve);
        ssc.data_set_number(data, 'wind_turbine_hub_ht', self.hub_height_meters)
        ssc.data_set_number(data, 'wind_turbine_max_cp', 0.44999998807907104)
        wind_farm_xCoordinates = [0]
        ssc.data_set_array(data, 'wind_farm_xCoordinates', wind_farm_xCoordinates)
        wind_farm_yCoordinates = [0]
        ssc.data_set_array(data, 'wind_farm_yCoordinates', wind_farm_yCoordinates)
        ssc.data_set_number(data, 'wind_farm_losses_percent', 0)
        ssc.data_set_number(data, 'wind_farm_wake_model', 0)
        ssc.data_set_number(data, 'adjust:constant', 0)

        self.ssc = ssc
        self.data = data
        self.module = module
        self.wind_resource = wind_resource


    def wind_prod_factor(self):

        #wind_resource = self.ssc.data_get_table(self.data, 'wind_resource_data')
        #data = self.ssc.data_get_matrix(wind_resource, 'data')

        if self.ssc.module_exec(self.module, self.data) == 0:
            print ('windpower simulation error')
            idx = 1
            msg = self.ssc.module_log(self.module, 0)
            while msg is not None:
                print ('	: ' + msg)
                msg = self.ssc.module_log(self.module, idx)
                idx = idx + 1
        self.ssc.module_free(self.module)

        # the system_power output from SAMSDK is of same length as input (i.e. 35040 series for 4 times steps/hour)
        system_power = self.ssc.data_get_array(self.data, 'gen')
        prod_factor_original = [power/self.system_capacity for power in system_power]
        self.ssc.data_free(self.data)
        if self.use_input_data:
            self.ssc.data_free(self.wind_resource)

        # subhourly (i.e 15 minute data)
        if self.time_steps_per_hour >= 1:
            timesteps = []
            timesteps_base = range(0, 8760)
            for ts_b in timesteps_base:
                for step in range(0, self.time_steps_per_hour):
                    timesteps.append(ts_b)

        # downscaled run (i.e 288 steps per year)
        else:
            timesteps = range(0, 8760, int(1 / self.time_steps_per_hour))

        prod_factor = []

        for hour in timesteps:
            #prod_factor.append(round(prod_factor_original[hour]/self.time_steps_per_hour, 3))
            prod_factor.append(prod_factor_original[hour])

        return prod_factor_original

    def combine_files(self, file_resource_heights, file_combined):
        data = [None] * 2
        for height, f in file_resource_heights.iteritems():
            if os.path.isfile(f):
                with open(f) as file_in:
                    csv_reader = csv.reader(file_in, delimiter=',')
                    line = 0
                    for row in csv_reader:
                        if line < 2:
                            data[line] = row
                        else:
                            if line >= len(data):
                                data.append(row)
                            else:
                                data[line] += row
                        line += 1

        with open(file_combined, 'w') as file_out:
            writer = csv.writer(file_out)
            writer.writerows(data)

        return os.path.isfile(file_combined)