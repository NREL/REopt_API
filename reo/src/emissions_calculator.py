import os
import json
import logging
log = logging.getLogger(__name__)
import geopandas as gpd
import pandas as pd
import numpy as np
from functools import partial
import pyproj
from shapely.ops import nearest_points
from shapely import geometry as g
from shapely.ops import transform


class EmissionsCalculator:

    def __init__(self, latitude=None, longitude=None, time_steps_per_hour=1, **kwargs):
        """
        :param latitude: float
        :param longitude: float
        :param kwargs:
        """
        self._region_lookup = None
        self.library_path = os.path.join('reo', 'src', 'data')
        self.latitude = float(latitude) if latitude is not None else None
        self.longitude = float(longitude) if longitude is not None else None
        self.time_steps_per_hour = time_steps_per_hour
        self._region_abbr = None
        self._emmissions_profile = None
        self._transmission_and_distribution_losses = None
        self.meters_to_region = None
        
        proj102008 = pyproj.Proj("+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs")
        self.project4326_to_102008 = partial(pyproj.transform,pyproj.Proj(init='epsg:4326'),proj102008)
    
    @staticmethod
    def add_to_data(data):

        if 'Emissions Warning' in (data['messages'].get('warnings') or {}).keys():
            data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_C02'] = None
            data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_C02'] = None
            data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_C02'] = None
            data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_C02'] = None
            data['outputs']['Scenario']['Site']['year_one_emissions_lb_C02'] = None
            data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_C02'] = None
            return data
        
        else:
            precision = 1
            cannot_calc_total_emissions = False
            cannot_calc_bau_total_emissions = False
            missing_emissions = []

            time_steps_per_hour = data['inputs']['Scenario']['time_steps_per_hour']
            
            data['outputs']['Scenario']['Site']['year_one_emissions_lb_C02'] = 0
            data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_C02'] = 0
            
            hourly_emissions = np.array(data['inputs']['Scenario']['Site']['ElectricTariff']['emissions_factor_series_lb_CO2_per_kwh'])
            from_utility_series = np.array(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_load_series_kw') \
                or [0 for _ in range(8760 *time_steps_per_hour)]) + \
                np.array(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_battery_series_kw') or \
                [0 for _ in range(8760 * time_steps_per_hour)]) 

            if hourly_emissions.shape[0] > 0:
                data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_C02'] = \
                round((hourly_emissions * from_utility_series).sum(),precision)
                
                data['outputs']['Scenario']['Site']['year_one_emissions_lb_C02'] += \
                round(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_C02'],precision)

                loads_kw = np.array(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_to_load_series_bau_kw'] or [])
                if len(loads_kw) == 0:
                    loads_kw = 0
                data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_C02'] = \
                    round((hourly_emissions * loads_kw).sum(),precision)
                data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_C02'] += \
                    round(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_C02'],precision)
            else:
                if (sum(from_utility_series) > 0):
                    cannot_calc_total_emissions = True
                    missing_emissions.append('ElectricTariff')
                else:
                    data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_C02'] = 0

                if (sum(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_load_bau_series_kw') or [0]) > 0):
                    cannot_calc_bau_total_emissions = True
                    missing_emissions.append('ElectricTariff')
                else:
                    data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_C02'] = 0
            
            generator_emmissions = data['inputs']['Scenario']['Site']['Generator'].get('emissions_factor_lb_CO2_per_gal')
            if generator_emmissions is not None:
                data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_C02'] = \
                round(generator_emmissions * data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal") or 0,precision)
                data['outputs']['Scenario']['Site']['year_one_emissions_lb_C02'] += \
                round(data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_C02'],precision)
                
                data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_C02'] = \
                round(generator_emmissions *  data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal_bau") or 0,precision)
                data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_C02'] += \
                round(data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_C02'],precision)
                            
            else:
                if data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal") or 0 > 0:
                    cannot_calc_total_emissions = True
                    missing_emissions.append('Generator')
                else:
                    data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_C02'] = 0

                if data['outputs']['Scenario']['Site']['Generator'].get('fuel_used_gal_bau') or 0 > 0:
                    cannot_calc_bau_total_emissions = True
                    missing_emissions.append('Generator')
                else:
                    data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_C02'] = 0
            
            if cannot_calc_total_emissions:
                data['outputs']['Scenario']['Site']['year_one_emissions_lb_C02'] = None

            if cannot_calc_bau_total_emissions:
                data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_C02'] = None
            
            if cannot_calc_bau_total_emissions or cannot_calc_total_emissions:
                
                message  = 'Could not calculate Site level emissions'
                if cannot_calc_total_emissions:
                    message += ' for optimized results'
                if cannot_calc_bau_total_emissions:
                    if cannot_calc_total_emissions:
                        message += ' or'
                    message += ' for BAU case'
                
                message += '. Missing an emission factor for the following: {}'.format(','.join(set(missing_emissions)))

                if 'messages' not in data.keys():
                    data['messages'] = {"warnings":{}}
                if 'warnings' not in data['messages'].keys():
                    data['messages']["warnings"] = {}
                data['messages']['warnings']['Emissions Warning'] = message
                
        return data

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
                    raise AttributeError("Could look up AVERT emissions region from point ({},{}). Location is\
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
            df = pd.read_csv(os.path.join(self.library_path,'AVERT_hourly_emissions.csv'))
            if self.region_abbr in df.columns:
                self._emmissions_profile = list(df[self.region_abbr].round(3).values)
                if self.time_steps_per_hour > 1:
                    self._emmissions_profile = list(np.concatenate([[i]*self.time_steps_per_hour for i in self._emmissions_profile]))
            else:
                raise AttributeError("Emissions error. Cannnot find hourly emmissions for region {} ({},{}) \
                    ".format(self.region, self.latitude,self.longitude))
        return self._emmissions_profile