"""
sample Python codes for EASIUR and APSCA
"""

import csv
import deepdish
import h5py
import numpy as np
import pyproj
import os

# print(f"This module uses the following packages")
# print(f"deepdish: {deepdish.__version__}")
# print(f"h5py    : {h5py.__version__}")
# print(f"numpy   : {np.__version__}")
# print(f"pyproj  : {pyproj.__version__}")

library_path = os.path.join('reo', 'src', 'data')

# Income Growth Adjustment factors from BenMAP
MorIncomeGrowthAdj = {
    1990: 1.000000,
    1991: 0.992025,
    1992: 0.998182,
    1993: 1.003087,
    1994: 1.012843,
    1995: 1.016989,
    1996: 1.024362,
    1997: 1.034171,
    1998: 1.038842,
    1999: 1.042804,
    2000: 1.038542,
    2001: 1.043834,
    2002: 1.049992,
    2003: 1.056232,
    2004: 1.062572,
    2005: 1.068587,
    2006: 1.074681,
    2007: 1.080843,
    2008: 1.087068,
    2009: 1.093349,
    2010: 1.099688,
    2011: 1.111515,
    2012: 1.122895,
    2013: 1.133857,
    2014: 1.144425,
    2015: 1.154627,
    2016: 1.164482,
    2017: 1.174010,
    2018: 1.183233,
    2019: 1.192168,
    2020: 1.200834,
    2021: 1.209226,
    2022: 1.217341,
    2023: 1.225191,
    2024: 1.232790,
}

# GDP deflator from BenMAP
GDP_deflator = {
    1980: 0.478513,
    1981: 0.527875,
    1982: 0.560395,
    1983: 0.578397,
    1984: 0.603368,
    1985: 0.624855,
    1986: 0.636469,
    1987: 0.659698,
    1988: 0.686992,
    1989: 0.720093,
    1990: 0.759001,
    1991: 0.790941,
    1992: 0.814750,
    1993: 0.839141,
    1994: 0.860627,
    1995: 0.885017,
    1996: 0.911150,
    1997: 0.932056,
    1998: 0.946574,
    1999: 0.967480,
    2000: 1.000000,
    2001: 1.028455,
    2002: 1.044715,
    2003: 1.068525,
    2004: 1.096980,
    2005: 1.134146,
    2006: 1.170732,
    2007: 1.204077,
    2008: 1.250308,
    2009: 1.245860,
    2010: 1.266295,
}

# pyproj constant
# LCP_US = pyproj.Proj("+proj=lcc +no_defs +a=6370000.0m +b=6370000.0m \
#                    +lon_0=97w +lat_0=40n +lat_1=33n +lat_2=45n \
#                    +x_0=2736000.0m +y_0=2088000.0m +towgs84=0,0,0")
# GEO_SPHEROID = pyproj.Proj("+proj=lonlat +towgs84=0,0,0 +a=6370000.0m +no_defs")
LCP_US = pyproj.Proj(
    "+proj=lcc +no_defs +a=6370000.0 +b=6370000.0 "
    "+lon_0=97w +lat_0=40n +lat_1=33n +lat_2=45n "
    "+x_0=2736000.0 +y_0=2088000.0 +to_wgs=0,0,0 +units=m"
)
# GEO_SPHEROID = pyproj.Proj("+proj=lonlat +towgs84=0,0,0 +a=6370000.0 +no_defs")
DATUM_NAD83 = pyproj.Proj("+init=epsg:4269 +proj=longlat +ellps=GRS80 +datum=NAD83 +no_defs +towgs84=0,0,0")
DATUM_WGS84 = pyproj.Proj("+init=epsg:4326 +proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs +towgs84=0,0,0")


def get_EASIUR2005(stack, pop_year=2005, income_year=2005, dollar_year=2010):
    """Returns EASIUR for a given `stack` height in a dict.

    Args:
        stack: area, p150, p300
        pop_year: population year
        income_year: income level (1990 to 2024)
        dollar_year: dollar year (1980 to 2010)
    """

    if stack not in ["area", "p150", "p300"]:
        print("stack should be one of 'area', 'p150', 'p300'")
        return False

    file_2005 = "sc_8.6MVSL_" + stack + "_pop2005.hdf5"

    #ret_map = deepdish.io.load("data/EASIUR_Data/" + file_2005)
    ret_map = deepdish.io.load(os.path.join(library_path, 'EASIUR_Data', file_2005))

    if pop_year != 2005:
        filename = "sc_growth_rate_pop2005_pop2040_" + stack + ".hdf5"
        map_rate = deepdish.io.load(os.path.join(library_path, 'EASIUR_Data', filename))

        for k, v in map_rate.items():
            ret_map[k] = ret_map[k] * (v ** (pop_year - 2005))

    if income_year != 2005:
        try:
            adj = MorIncomeGrowthAdj[income_year] / MorIncomeGrowthAdj[2005]
            for k, v in ret_map.items():
                ret_map[k] = v * adj
        except KeyError:
            print("income year must be between 1990 to 2024")
            return False

    if dollar_year != 2010:
        try:
            adj = GDP_deflator[dollar_year] / GDP_deflator[2010]
            for k, v in ret_map.items():
                ret_map[k] = v * adj
        except KeyError:
            print("Dollar year must be between 1980 to 2010")
            return False

    return ret_map


def get_pop_inc(year, min_age=30):
    """Returns population and incidence (or mortality) rate of `min_age` or older for a given `year`."""

    remainder = int(year) % 5
    if remainder == 0:
        return get_pop_inc_raw(year, min_age)
    else:
        # linear interpolation
        p1, i1 = get_pop_inc_raw(year - remainder, min_age)
        p2, i2 = get_pop_inc_raw(year - remainder + 5, min_age)
        pop = (p1 * (5 - remainder) + p2 * remainder) / 5.0
        inc = (i1 * (5 - remainder) + i2 * remainder) / 5.0
        return pop, inc


def get_pop_inc_raw(year, min_age=30):
    """Returns population and incidence (or mortality) rate of `min_age` or older for a given `year`.

    Raw data (CSV files) were derived from BenMAP
    """

#    with open("data/EASIUR_Data/PopInc/popinc" + str(year) + ".CSV", newline="") as f:
    with open(os.path.join(library_path, 'EASIUR_Data/PopInc/popinc{}.CSV'.format(str(year))), newline="") as f:
        
        pop = np.zeros((148, 112))
        inc = np.zeros((148, 112))
        popinc_csv = csv.reader(f)
        header = next(popinc_csv)

        if "Col" in header[0]:  # Col has a strange char
            header[0] = "Col"

        xys = set()
        for row in popinc_csv:
            row_d = dict(zip(header, row))
            if int(row_d["Start Age"]) == min_age:
                x = int(row_d["Col"]) - 1
                y = int(row_d["Row"]) - 1
                if (x, y) in xys:
                    # just to check
                    print("Duplicate?", x, y)
                xys.add((x, y))
                p = float(row_d["Population"])
                i = float(row_d["Baseline"])
                # print float(row_d['Point Estimate'])/i, row_d['Percent of Baseline']
                pop[x, y] = p
                inc[x, y] = i / p
        return pop, inc


def get_avg_plume(x, y, spec, stack="area", season="Q0"):
    """Returns an Average Plume in a 148x112 array

    Args:
        x, y: source location
        spec: species (PEC, SO2, NOX, NH3)
        stack: stack height (area, p150, p300)
        season: season (Q0 for Annual, Q1 for Jan-Mar, Q2 for Apr-Jun, Q3 for Jul-Sep, Q4 for Oct-Dec)

    Returns:
        an average plume in a 148x112 array
    """

    h5f = "".join(
        ["data/EASIUR_Data/AveragePlumes_181x181/avgplumes_", season, "_", str(stack) + ".hdf5"]
    )
    with h5py.File(h5f) as f:
        return f[spec][x, y]


def get_avg_plume_stack(x, y, stkht, spec, season="Q0"):
    """Returns an Average Plume in a 148x112 array"""

    stkht = float(stkht)

    # linear interpolation
    if stkht < 150:
        ap1 = get_avg_plume(x, y, spec, stack="area", season=season)
        ap2 = get_avg_plume(x, y, spec, stack="p150", season=season)
        return ap1 * (1 - stkht / 150.0) + ap2 * stkht / 150.0
    elif stkht < 300:
        ap2 = get_avg_plume(x, y, spec, stack="p150", season=season)
        ap3 = get_avg_plume(x, y, spec, stack="p300", season=season)
        return ap2 * (1 - (stkht - 150.0) / 150.0) + ap3 * (stkht - 150.0) / 150.0
    else:
        ap3 = get_avg_plume(x, y, spec, stack="p300", season=season)
        return ap3


def l2g(x, y, inverse=False, datum="NAD83"):
    """Convert LCP (x, y) in CAMx 148x112 grid to Geodetic (lon, lat)"""

    if datum == "NAD83":
        datum = DATUM_NAD83
    elif datum == "WGS84":
        datum = DATUM_WGS84

    if inverse:
        return np.array(pyproj.transform(datum, LCP_US, x, y)) / 36000.0 + np.array(
            [1, 1]
        )
    else:
        return pyproj.transform(LCP_US, datum, (x - 1) * 36e3, (y - 1) * 36e3)


def g2l(lon, lat, datum="NAD83"):
    """Convert Geodetic (lon, lat) to LCP (x, y) in CAMx 148x112 grid"""
    return l2g(lon, lat, True, datum)
