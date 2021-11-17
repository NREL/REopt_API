import os
import json
import logging
log = logging.getLogger(__name__)
import geopandas as gpd
import pandas as pd
import numpy as np
from functools import partial
import pyproj
from reo.src.pyeasiur import *

from shapely import geometry as g
from shapely.ops import transform

class EmissionsCalculator:

    def __init__(self, latitude=None, longitude=None, pollutant=None, **kwargs):
        """
        :param latitude: float
        :param longitude: float
        :param kwargs:
        """
        self._region_lookup = None
        self.library_path = os.path.join('reo', 'src', 'data')
        self.latitude = float(latitude) if latitude is not None else None
        self.longitude = float(longitude) if longitude is not None else None
        self.pollutant = pollutant
        self._region_abbr = None
        self._emmissions_profile = None
        self._transmission_and_distribution_losses = None
        self.meters_to_region = None
        self.time_steps_per_hour = kwargs.get('time_steps_per_hour') or 1
        proj102008 = pyproj.Proj("+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs")
        self.project4326_to_102008 = partial(pyproj.transform,pyproj.Proj(init='epsg:4326'),proj102008)
    
    @property
    def region(self):
        lookup = {  'AK':'Alaska',
                    'CA':'California',
                    'EMW':'Great Lakes / Atlantic',
                    'NE': 'Northeast',
                    'NW':'Northwest',
                    'RM':'Rocky Mountains',
                    'SC':'Lower Midwest',
                    'SE': 'Southeast',
                    'SW':'Southwest',
                    'TX':'Texas',
                    'WMW':'Upper Midwest',
                    'HI':'Hawaii (except Oahu)',
                    'HI-Oahu':'Hawaii (Oahu)' }
        
        if self.region_abbr is not None:
            return lookup[self.region_abbr]
        return None
    
    @property
    def region_abbr(self):
        if self._region_abbr is None:
            gdf = gpd.read_file(os.path.join(self.library_path,'avert_4326.shp'))

            gdf_query = gdf[gdf.geometry.intersects(g.Point(self.longitude, self.latitude))]
            if not gdf_query.empty:
                self.meters_to_region = 0
                self._region_abbr = gdf_query.AVERT.values[0]
                
            if self._region_abbr is None:
                gdf = gpd.read_file(os.path.join(self.library_path,'avert_102008.shp'))
                try:
                    lookup = transform(self.project4326_to_102008, g.Point(self.longitude, self.latitude))
                except:
                    raise AttributeError("Could not look up AVERT emissions region from point ({},{}). Location is\
                        likely invalid or well outside continental US, AK and HI".format(self.longitude, self.latitude))
                distances_meter = gdf.geometry.apply(lambda x : x.distance(lookup)).values
                min_idx = list(distances_meter).index(min(distances_meter))
                self._region_abbr = gdf.loc[min_idx,'AVERT']
                self.meters_to_region = int(round(min(distances_meter)))
                if self.meters_to_region > 8046:
                    raise AttributeError('Your site location ({},{}) is more than 5 miles from the '
                        'nearest emission region. Cannot calculate emissions.'.format(self.longitude, self.latitude))
        return self._region_abbr
    
    @property
    def emissions_series(self):
        if self._emmissions_profile is None:
            df = pd.read_csv(os.path.join(self.library_path,'AVERT_hourly_emissions_{}.csv'.format(self.pollutant)), dtype='float64', float_precision='high')
            if self.region_abbr in df.columns:
                self._emmissions_profile = list(df[self.region_abbr].round(6).values)
                if self.time_steps_per_hour > 1:
                    self._emmissions_profile = list(np.concatenate([[i] * self.time_steps_per_hour for i in self._emmissions_profile]))
            else:
                raise AttributeError("Emissions error. Cannnot find hourly emmissions for region {} ({},{}) \
                    ".format(self.region, self.latitude,self.longitude)) 
        return self._emmissions_profile


class EASIURCalculator:

    def __init__(self, latitude=None, longitude=None, **kwargs):
        """
        :param latitude: float
        :param longitude: float
        :param kwargs:
        """
        self.library_path = os.path.join('reo', 'src', 'data')
        self.latitude = float(latitude) if latitude is not None else None
        self.longitude = float(longitude) if longitude is not None else None
        self.inflation = kwargs.get('inflation') or None
        self._grid_costs_per_tonne = None
        self._onsite_costs_per_tonne = None
        self._escalation_rates = None 
        
    
    @property
    def grid_costs(self):
        if self._grid_costs_per_tonne is None:
            # Assumption: grid emissions occur at site at 150m above ground;
            EASIUR_150m = get_EASIUR2005('p150', pop_year=2020, income_year=2020, dollar_year=2010)  # For keys in EASIUR: EASIUR_150m_pop2020_inc2020_dol2010.keys()

            # convert lon, lat to CAMx grid (x, y), specify datum. default is NAD83
            # Note: x, y returned from g2l follows the CAMx grid convention.
            # x and y start from 1, not zero. (x) ranges (1, ..., 148) and (y) ranges (1, ..., 112)
            x, y = g2l(self.longitude, self.latitude, datum='NAD83')
            x = int(round(x))
            y = int(round(y))

            # Convert from 2010$ to 2020$ (source: https://www.in2013dollars.com/us/inflation/2010?amount=100)
            convert_2010_2020_usd = 1.246
            try:
                self._grid_costs_per_tonne = {
                    'NOx': EASIUR_150m['NOX_Annual'][x - 1, y - 1] * convert_2010_2020_usd,
                    'SO2': EASIUR_150m['SO2_Annual'][x - 1, y - 1] * convert_2010_2020_usd,
                    'PM25': EASIUR_150m['PEC_Annual'][x - 1, y - 1] * convert_2010_2020_usd,
                }
            except:
                raise AttributeError("Could not look up EASIUR health costs from point ({},{}). Location is \
                    likely invalid or outside the CAMx grid".format(self.latitude, self.longitude))
        return self._grid_costs_per_tonne

    @property
    def onsite_costs(self):
        if self._onsite_costs_per_tonne is None:
            # Assumption: on-site fuelburn emissions occur at site at 0m above ground;
            EASIUR_0m = get_EASIUR2005('area', pop_year=2020, income_year=2020, dollar_year=2010)  # For keys in EASIUR: EASIUR_150m_pop2020_inc2020_dol2010.keys()

            # convert lon, lat to CAMx grid (x, y), specify datum. default is NAD83
            # Note: x, y returned from g2l follows the CAMx grid convention.
            # x and y start from 1, not zero. (x) ranges (1, ..., 148) and (y) ranges (1, ..., 112)
            x, y = g2l(self.longitude, self.latitude, datum='NAD83')
            x = int(round(x))
            y = int(round(y))

            # Convert from 2010$ to 2020$ (source: https://www.in2013dollars.com/us/inflation/2010?amount=100)
            convert_2010_2020_usd = 1.246
            try:
                self._onsite_costs_per_tonne = {
                    'NOx': EASIUR_0m['NOX_Annual'][x - 1, y - 1] * convert_2010_2020_usd,
                    'SO2': EASIUR_0m['SO2_Annual'][x - 1, y - 1] * convert_2010_2020_usd,
                    'PM25': EASIUR_0m['PEC_Annual'][x - 1, y - 1] * convert_2010_2020_usd,
                }
            except:
                raise AttributeError("Could not look up EASIUR health costs from point ({},{}). Location is \
                    likely invalid or outside the CAMx grid".format(self.latitude, self.longitude))
        return self._onsite_costs_per_tonne

    @property
    def escalation_rates(self):
        if self._escalation_rates is None:
            EASIUR_150m_yr2020 = get_EASIUR2005('p150', pop_year=2020, income_year=2020, dollar_year=2010) 
            EASIUR_150m_yr2024 = get_EASIUR2005('p150', pop_year=2024, income_year=2024, dollar_year=2010) 

            # convert lon, lat to CAMx grid (x, y), specify datum. default is NAD83
            x, y = g2l(self.longitude, self.latitude, datum='NAD83')
            x = int(round(x))
            y = int(round(y))

            try:
                # real compound annual growth rate
                cagr_real = { 
                    'NOx': (EASIUR_150m_yr2024['NOX_Annual'][x - 1, y - 1]/EASIUR_150m_yr2020['NOX_Annual'][x - 1, y - 1])**(1/4)-1,
                    'SO2': (EASIUR_150m_yr2024['SO2_Annual'][x - 1, y - 1]/EASIUR_150m_yr2020['SO2_Annual'][x - 1, y - 1])**(1/4)-1,
                    'PM25': (EASIUR_150m_yr2024['PEC_Annual'][x - 1, y - 1]/EASIUR_150m_yr2020['PEC_Annual'][x - 1, y - 1])**(1/4)-1,
                }
                # nominal compound annual growth rate (real + inflation)
                self._escalation_rates = {
                    'NOx': cagr_real['NOx'] + self.inflation,
                    'SO2': cagr_real['SO2'] + self.inflation,
                    'PM25': cagr_real['PM25'] + self.inflation,
                }
            except:
                raise AttributeError("Could not look up EASIUR health costs from point ({},{}). Location is \
                    likely invalid or outside the CAMx grid".format(self.latitude, self.longitude))
        return self._escalation_rates
