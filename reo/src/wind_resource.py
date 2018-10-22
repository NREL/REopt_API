import h5pyd
from pyproj import Proj
import numpy as np
import pandas as pd
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

hub_height_strings = {
    20: "windspeed_20m",  # residential?
    40: "windspeed_40m",  # commercial
    60: "windspeed_60m",  # medium
    80: "windspeed_80m",  # large
    100: "windspeed_100m",
}
frequency_map = {  # time_steps_per_hour to pandas sampling frequency string
    2: '30T',
    4: '15T',
}


def get_conic_coords(db_conn, lat, lng):
    """
    Convert latitude, longitude into integer values for wind tool kit database.
    Modified from "indicesForCoord" in https://github.com/NREL/hsds-examples/blob/master/notebooks/01_introduction.ipynb
    Questions? Perr-Sauer, Jordan <Jordan.Perr-Sauer@nrel.gov>
    :param db_conn: h5pyd.File, database connection
    :param latitude:
    :param longitude:
    :return: (y, x) values to index into db_conn
    """
    dset_coords = db_conn['coordinates']
    projstring = """+proj=lcc +lat_1=30 +lat_2=60 
                    +lat_0=38.47240422490422 +lon_0=-96.0 
                    +x_0=0 +y_0=0 +ellps=sphere 
                    +units=m +no_defs """
    projectLcc = Proj(projstring)
    origin_ll = reversed(dset_coords[0][0])  # Grab origin directly from database
    origin = projectLcc(*origin_ll)

    coords = projectLcc(lng, lat)
    delta = np.subtract(coords, origin)
    ij = [int(round(x / 2000)) for x in delta]
    return tuple(reversed(ij))


def get_wind_resource(latitude, longitude, hub_height_meters, time_steps_per_hour=1):
    """
    Download hourly wind speeds for location and hub height, and resample if time_steps_per_hour != 1
    :param latitude:
    :param longitude:
    :param hub_height_meters:
    :param time_steps_per_hour: int, 1, 2, or 4
    :return: list with length = 8760 * time_steps_per_hour, wind_meters_per_sec
    """
    db_conn = h5pyd.File("/nrel/wtk-us.h5", 'r')
    y, x = get_conic_coords(db_conn, latitude, longitude)
    """
    Note: we add one hourly value to wind resource when querying the database for interpolating to higher time 
    resolutions. The last value must be dropped even if upsampling occurs.
    """
    hourly_wind_meters_per_sec = db_conn[hub_height_strings[hub_height_meters]][43824:52584+1, y, x]

    if time_steps_per_hour != 1:  # upsample data
        index = pd.date_range('1/1/2018', periods=8761, freq='H')
        series = pd.Series(hourly_wind_meters_per_sec, index=index)
        series = series.resample(frequency_map[time_steps_per_hour]).interpolate(method='linear')
        wind_meters_per_sec = series.tolist()[:-1]  # see Note above about dropping last value
    else:
        wind_meters_per_sec = list(hourly_wind_meters_per_sec[:-1])  # see Note above about dropping last value

    wind_meters_per_sec = [float(x) for x in wind_meters_per_sec]  # numpy float32 is not json serializable

    return wind_meters_per_sec
