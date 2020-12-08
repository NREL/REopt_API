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
import csv
import numpy as np
import os
from .sscapi import PySSC

"""
Generic NREL powercurves for different scales of turbines as defined in SAM as
- NREL 2000kW Distributed Large Turbine Reference
- NREL 250kW Distributed Midsize Turbine Reference
- NREL 100kW Distributed Commercial Turbine Reference
- NREL 2.5kW Distributed Residential Turbine Reference

"""
wind_turbine_powercurve_lookup = {'large': [0, 0, 0, 70.119, 166.208, 324.625, 560.952, 890.771, 1329.664,
                                            1893.213, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000,
                                            2000, 2000, 2000, 2000, 2000, 2000],
                                  'medium': [0, 0, 0, 8.764875, 20.776, 40.578125, 70.119, 111.346375, 166.208,
                                             236.651625, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250,
                                             250, 250, 250, 250, 250],
                                  'commercial': [0, 0, 0, 3.50595, 8.3104, 16.23125, 28.0476, 44.53855, 66.4832,
                                                 94.66065, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
                                                 100, 100, 100, 100, 100],
                                  'residential': [0, 0, 0, 0.070542773, 0.1672125, 0.326586914, 0.564342188,
                                                  0.896154492, 1.3377, 1.904654883, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                                                  2.5, 2.5, 2.5, 0, 0, 0, 0, 0, 0, 0]}

"""
Corresponding size in kW for generic reference turbines sizes
"""
system_capacity_lookup = {'large': 2000,
                          'medium': 250,
                          'commercial': 100,
                          'residential': 2.5}


"""
Corresponding rotor diameter in meters for generic reference turbines sizes
"""
rotor_diameter_lookup = {'large': 55*2,
                         'medium': 21.9*2,
                         'commercial': 13.8*2,
                         'residential': 1.85*2}


"""
Corresponding string interval name given a float time step in hours
"""
time_step_hour_to_minute_interval_lookup = {
    round(float(1), 2): '60',
    round(float(0.5), 2): '30',
    round(float(0.25), 2): '15',
    round(float(5/60), 2): '5',
    round(float(1/60), 2): '1'}


"""
Allowed hub heights in meters for the Wind Toolkit
"""
allowed_hub_height_meters = [10, 40, 60, 80, 100, 120, 140, 160, 200]


"""
Given a dictionary of heights and filenames, combine into one resource file

Parameters
----------
file_resource_heights: dict
    Dictionary with key as height in meters, value as absolute path to resource file, eg
    {40: '/local/workspace/39.9_-105.2_windtoolkit_2012_60_min_40m.srw',
     60: '/local/workspace/39.9_-105.2_windtoolkit_2012_60_min_60m.srw'}
file_combined: string
    The filename to combine the resource data into, eg:
    '/local/workspace/39.9_-105.2_windtoolkit_2012_60_min_40m_60m.srw
"""
def combine_wind_files(file_resource_heights, file_combined):
    data = [None] * 2
    for height, f in file_resource_heights.items():
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

    with open(file_combined, 'w') as fo:
        writer = csv.writer(fo)
        writer.writerows(data)

    return os.path.isfile(file_combined)


class WindSAMSDK:
    """
    Class to manage interaction with the SAM wind model through the softwawre development kit (SDK)
    User can interact with class with resource data in the following ways:
    1. Pass in vectors of temperature, pressure, wind speed, wind direction
    2. Pass in a resource file directly: file_resource_full
    3. Utilize the wind toolkit API, which will download required data if none passed in

    Attributes
    ----------
    wind_turbine_speeds: list
        The speeds corresponding to all turbine power curves
    elevation: float
        Site elevation in meters
    latitude: float
        Site latitude
     longitude: float
        Site longitude
     year: int
        The year of resource data
     size_class: string
        The size class of the turbine
     hub_height_meters: float
        The desired turbine height
    time_steps_per_hour: float
        The time interval, eg. 1 is hourly, 0.5 half hour
    file_resource_full: string
        Absolute path of filename (.srw file) with all heights necessary
    """

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
                 file_resource_full=None,
                 **kwargs
                 ):
        """
        Parameters
        ----------
        path_inputs: string
            Path to folder where resource data should download
        hub_height_meters: float
            The desired turbine height
        elevation: float
            Site elevation in meters
        latitude: float
            Site latitude
         longitude: float
            Site longitude
         year: int
            The year of resource data
         size_class: string
            The size class of the turbine
         temperature_celsius: list
            If passing in data directly, the list of temperatures at the hub height
         pressure_atmospheres: list
            If passing in data directly, the list of pressures at the hub height
         wind_meters_per_sec: list
            If passing in data directly, the list of wind speeds at the hub height
         wind_direction_degrees: list
            If passing in data directly, the list of directions at the hub height
        time_steps_per_hour: float
            The time interval, eg. 1 is hourly, 0.5 half hour
        file_resource_full: string
            Absolute path of filename (.srw file) with all heights necessary
        """

        self.elevation = elevation
        self.latitude = latitude
        self.longitude = longitude
        self.year = year
        self.size_class = size_class
        self.hub_height_meters = hub_height_meters
        self.time_steps_per_hour = time_steps_per_hour
        self.interval = time_step_hour_to_minute_interval_lookup[round(float(time_steps_per_hour), 2)]
        self.use_input_data = False

        if file_resource_full is not None:
            self.file_resource_full = file_resource_full
            self.file_downloaded = os.path.isfile(self.file_resource_full)

        # If data vectors have been passed in
        if None not in [temperature_celsius, pressure_atmospheres, wind_direction_degrees, wind_meters_per_sec]:
            self.temperature_celsius = temperature_celsius
            self.pressure_atmospheres = pressure_atmospheres
            self.wind_direction_degrees = wind_direction_degrees
            self.wind_meters_per_sec = wind_meters_per_sec
            self.use_input_data = True

        # If we need to download the resource data
        elif file_resource_full is None or not self.file_downloaded:
            # TODO: check input_files for previously downloaded wind resource file
            from reo.src.wind_resource import get_wind_resource_developer_api

            # evaluate hub height, determine what heights of resource data are required
            heights = [hub_height_meters]
            if hub_height_meters not in allowed_hub_height_meters:
                height_low = allowed_hub_height_meters[0]
                height_high = allowed_hub_height_meters[-1]
                for h in allowed_hub_height_meters:
                    if h < hub_height_meters:
                        height_low = h
                    elif h > hub_height_meters:
                        height_high = h
                        break
                heights[0] = height_low
                heights.append(height_high)

            # if there is no resource file passed in, create one
            if file_resource_full is None:
                file_resource_base = os.path.join(path_inputs,
                                                  str(latitude) + "_" + str(longitude) + "_windtoolkit_" + str(
                                                      year) + "_" + str(self.interval) + "min")
                file_resource_full = file_resource_base

            # Regardless of whether file passed in, create the intermediate files required to download
            file_resource_heights = {}
            for h in heights:
                file_resource_heights[h] = file_resource_base + '_' + str(h) + 'm.srw'
                file_resource_full += "_" + str(h) + 'm'
            file_resource_full += ".srw"

            for height, f in file_resource_heights.items():
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
                self.file_downloaded = combine_wind_files(file_resource_heights, file_resource_full)

        self.file_resource_full = file_resource_full
        self.wind_turbine_powercurve = wind_turbine_powercurve_lookup[size_class] 
        self.system_capacity = system_capacity_lookup[size_class] 
        self.rotor_diameter = rotor_diameter_lookup[size_class] 

        self.ssc = []
        self.data = []
        self.module = []
        self.wind_resource = []
        self.make_ssc()

    def make_ssc(self):
        """
        Function to set up the SAM run through the SAM Simulation Core
        """

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
            ssc.data_set_string(data, 'wind_resource_filename', self.file_resource_full)

        ssc.data_set_number(data, 'wind_resource_shear', 0.14000000059604645)
        ssc.data_set_number(data, 'wind_resource_turbulence_coeff', 0.10000000149011612)
        ssc.data_set_number(data, 'system_capacity', self.system_capacity)
        ssc.data_set_number(data, 'wind_resource_model_choice', 0)
        ssc.data_set_number(data, 'weibull_reference_height', 50)
        ssc.data_set_number(data, 'weibull_k_factor', 2)
        ssc.data_set_number(data, 'weibull_wind_speed', 7.25)
        ssc.data_set_number(data, 'wind_turbine_rotor_diameter', self.rotor_diameter)
        ssc.data_set_array(data, 'wind_turbine_powercurve_windspeeds', self.wind_turbine_speeds)
        ssc.data_set_array(data, 'wind_turbine_powercurve_powerout', self.wind_turbine_powercurve)
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
        """
        Retrieve the wind production factor, a time series unit representation of wind power production
        """

        if self.ssc.module_exec(self.module, self.data) == 0:
            print ('windpower simulation error')
            idx = 1
            msg = self.ssc.module_log(self.module, 0)
            while msg is not None:
                if type(msg) == bytes:
                    msg = msg.decode("utf-8")
                print ('   : {}'.format(msg))
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



