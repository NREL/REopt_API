import time
import h5pyd
from pyproj import Proj
import numpy as np
import pandas as pd
from reo.exceptions import UnexpectedError
from reo.log_levels import log 
"""
References: 
- https://www.nrel.gov/grid/wind-toolkit.html
- https://github.com/NREL/hsds-examples/

Requires a configuration file at ~/.hscfg with contents like so:

# HDFCloud configuration file
-hs_endpoint = https://developer.nrel.gov/api/hsds/ +v
-hs_username = None 
-hs_password = None 
-hs_api_key = <YOUR-API-KEY>  # from developer.nrel.gov


The h5pyd Files is indexed on [t, y, x], where:
    t is the integer hours since midnight on January 1st, 2007 up to 61368 for December 31st, 2013 (7 years of data) <- check this
    y, x are modified lambert conic coordinates
    
We use t values for 2012, since it is the closest year to the AMY data from AWS True Power, where:
    January 1st, 2012, 00:00:00 = 43824
    December 31st, 2012, 23:00:00 = 52608
However, since 2012 was a leap year, we only take the values through December 30th to get 8,760 values (52,584)
"""

hub_height_strings = {  # unused values included for potential future use
    10: "_10m",  # residential? - yes it is currently being used for residential
    40: "_40m",  # commercial
    60: "_60m",  # medium
    80: "_80m",  # large
    100: "_100m",
    120: "_120m",
    140: "_140m",
    160: "_160m",
    200: "_200m",
}
frequency_map = {  # time_steps_per_hour to pandas sampling frequency string
    2: '30T',
    3: '20T',
    4: '15T',
}

WTK_ORIGIN = (19.624062, -123.30661)
WTK_SHAPE = (1602, 2976)

def get_conic_coords(lat, lng):
    """
    Convert latitude, longitude into integer values for wind tool kit database.
    Modified from "indicesForCoord" in https://github.com/NREL/hsds-examples/blob/master/notebooks/01_introduction.ipynb
    Questions? Perr-Sauer, Jordan <Jordan.Perr-Sauer@nrel.gov>
    :param db_conn: h5pyd.File, database connection
    :param latitude:
    :param longitude:
    :return: (y, x) values to index into db_conn
    """
    #dset = h5pyd.File("/nrel/wtk-us.h5", 'r')['coordinates']
    projstring = """+proj=lcc +lat_1=30 +lat_2=60 
                    +lat_0=38.47240422490422 +lon_0=-96.0 
                    +x_0=0 +y_0=0 +ellps=sphere 
                    +units=m +no_defs """
    projectLcc = Proj(projstring)
    origin_ll = reversed(WTK_ORIGIN)  # origin_ll = reversed(dset[0][0])  to grab origin directly from database
    origin = projectLcc(*origin_ll)
    point = projectLcc(lng, lat)
    delta = np.subtract(point, origin)
    x,y = [int(round(x / 2000)) for x in delta]
    y_max, x_max = WTK_SHAPE # dset.shape to grab shape directly  from database
    if (x<0) or (y<0) or (x>=x_max) or (y>=y_max):
        raise ValueError("Latitude/Longitude is outside of wind resource dataset bounds.")
    return y,x

def get_wind_resource(latitude, longitude, hub_height_meters, time_steps_per_hour=1):
    """
    Download hourly wind speeds for location and hub height, and resample if time_steps_per_hour != 1
    :param latitude:
    :param longitude:
    :param hub_height_meters:
    :param time_steps_per_hour: int, 1, 2, or 4
    :return: list with length = 8760 * time_steps_per_hour, wind_meters_per_sec
    """

    pascals_to_atm = float(1.0 / 101325.0)
    kelvin_to_celsius = -273.15

    if hub_height_meters == 20:
        hub_height_meters = 10

    """
    import os
    filename = "wind_data.csv"
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        wind_meters_per_sec = df['windspeed'].tolist()[:-1]
        wind_direction_degrees = df['winddirection'].tolist()[:-1]
        temperature_kelvin = df['temperature'].tolist()[:-1]
        pressure_pascals = df['pressure_100m'].tolist()[:-1]
    """
    #else:

    def getWindData(name, start_i,end_i,y,x):
        numberTries = 0
        while numberTries < 20:
            try:
                with h5pyd.File("/nrel/wtk-us.h5", 'r') as hf:
                    return hf[name][start_i:end_i,y,x]
            except:
                print "wind dataset timed out {} times".format(numberTries+1)
                time.sleep(0.2)
                numberTries +=1
        log.error("Wind data download timed out")
        raise  ValueError('Wind Dataset Timed Out')


    y, x = get_conic_coords(latitude, longitude)
    #y, x = get_conic_coords(db_conn, latitude, longitude)
    
    """
    Note: we add one hourly value to wind resource when querying the database for interpolating to higher time 
    resolutions. The last value must be dropped even if upsampling occurs.
    """

    start_i = 43824
    end_i = 52584+1

    hourly_windspeed_meters_per_sec = getWindData('windspeed' + hub_height_strings[hub_height_meters],start_i,end_i,y,x)
    hourly_wind_direction_degrees = getWindData('winddirection' + hub_height_strings[hub_height_meters],start_i,end_i,y,x)
    hourly_temperature = getWindData('temperature' + hub_height_strings[hub_height_meters],start_i,end_i,y,x)
    hourly_pressure = getWindData('pressure_100m',start_i,end_i,y,x)
    
    if time_steps_per_hour != 1:  # upsample data

        index = pd.date_range('1/1/2018', periods=8761, freq='H')

        series = pd.Series(hourly_windspeed_meters_per_sec, index=index)
        series = series.resample(frequency_map[time_steps_per_hour]).interpolate(method='linear')
        wind_meters_per_sec = series.tolist()[:-1]  # see Note above about dropping last value

        series = pd.Series(hourly_wind_direction_degrees, index=index)
        series = series.resample(frequency_map[time_steps_per_hour]).interpolate(method='linear')
        wind_direction_degrees = series.tolist()[:-1]  # see Note above about dropping last value

        series = pd.Series(hourly_temperature, index=index)
        series = series.resample(frequency_map[time_steps_per_hour]).interpolate(method='linear')
        temperature_kelvin = series.tolist()[:-1]  # see Note above about dropping last value

        series = pd.Series(hourly_pressure, index=index)
        series = series.resample(frequency_map[time_steps_per_hour]).interpolate(method='linear')
        pressure_pascals = series.tolist()[:-1]  # see Note above about dropping last value

    else:
        wind_meters_per_sec = list(hourly_windspeed_meters_per_sec[:-1])  # see Note above about dropping last value
        wind_direction_degrees = list(hourly_wind_direction_degrees[:-1])
        temperature_kelvin = list(hourly_temperature[:-1])
        pressure_pascals = list(hourly_pressure[:-1])

    #d = {'windspeed': wind_meters_per_sec, 'winddirection': wind_direction_degrees, 'temperature': temperature_kelvin, 'pressure_100m': pressure_pascals}
    #df = pd.DataFrame(data=d)
    #df.to_csv(filename)

    wind_meters_per_sec = [float(x) for x in wind_meters_per_sec]  # numpy float32 is not json serializable
    wind_direction_degrees = [float(x) for x in wind_direction_degrees]
    temperature_celsius = [float(x) + kelvin_to_celsius for x in temperature_kelvin]
    pressure_atmospheres = [float(x) * pascals_to_atm for x in pressure_pascals]

    return {
        'wind_meters_per_sec': wind_meters_per_sec,
        'wind_direction_degrees': wind_direction_degrees,
        'temperature_celsius': temperature_celsius,
        'pressure_atmospheres': pressure_atmospheres,
    }
