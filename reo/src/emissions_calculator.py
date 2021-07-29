import os
import json
import logging
log = logging.getLogger(__name__)
import geopandas as gpd
import pandas as pd
import numpy as np
from functools import partial
import pyproj

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
    
    '''
    @staticmethod
    def add_to_data(data):

        precision = 1
        cannot_calc_total_emissions = False
        cannot_calc_bau_total_emissions = False
        missing_emissions = []

        
        data['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'] = 0
        data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'] = 0

        hourly_emissions = np.array(data['inputs']['Scenario']['Site']['ElectricTariff'].get('emissions_factor_series_lb_CO2_per_kwh') or [])
        from_utility_series = np.array(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_load_series_kw') \
            or [0 for _ in range(8760 *self.time_steps_per_hour)]) + \
            np.array(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_battery_series_kw') or \
            [0 for _ in range(8760 * self.time_steps_per_hour)]) 

        # If user supplies hourly CO2 emissions rates
        if hourly_emissions.shape[0] > 0:
            # Year one CO2 emissions from grid purchases (excludes exports)
            data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_CO2'] = \
            round((hourly_emissions * from_utility_series).sum(),precision)
            
            # Add to total Year 1 CO2 emissions
            data['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'] += \
            round(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_CO2'],precision)

            # BAU calcs
            loads_kw = np.array(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_to_load_series_bau_kw'] or [])
            if len(loads_kw) == 0:
                loads_kw = 0
            data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_CO2'] = \
                round((hourly_emissions * loads_kw).sum(),precision)
            data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'] += \
                round(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_CO2'],precision)
        
        # If user has not supplied CO2 emissions rates
        else:
            if (sum(from_utility_series) > 0): ## why is this > 0?
                cannot_calc_total_emissions = True
                missing_emissions.append('ElectricTariff')
            else:
                data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_CO2'] = 0

            if (sum(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_load_bau_series_kw') or [0]) > 0):
                cannot_calc_bau_total_emissions = True
                missing_emissions.append('ElectricTariff')
            else:
                data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_CO2'] = 0

        # Generator emissions
        generator_emmissions = data['inputs']['Scenario']['Site']['Generator'].get('emissions_factor_lb_CO2_per_gal')
        if generator_emmissions is not None:
            data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_CO2'] = \
                round(generator_emmissions * (data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal") or 0),precision)
            data['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'] += \
                round(data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_CO2'],precision)
            
            data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_CO2'] = \
                round(generator_emmissions *  (data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal_bau") or 0),precision)
            data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'] += \
                round(data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_CO2'],precision)
                        
        else:
            if data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal") or 0 > 0:
                cannot_calc_total_emissions = True
                missing_emissions.append('Generator')
            else:
                data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_CO2'] = 0

            if data['outputs']['Scenario']['Site']['Generator'].get('fuel_used_gal_bau') or 0 > 0:
                cannot_calc_bau_total_emissions = True
                missing_emissions.append('Generator')
            else:
                data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_CO2'] = 0
        
        # CHP emissions
        chp_emmissions = data['inputs']['Scenario']['Site']['CHP'].get('emissions_factor_lb_CO2_per_mmbtu')
        if chp_emmissions is not None:
            data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_lb_CO2'] = \
                round(chp_emmissions * (data['outputs']['Scenario']['Site']['CHP'].get("year_one_fuel_used_mmbtu") or 0),precision)
            data['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'] += \
                round(data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_lb_CO2'],precision)
            
        elif data['outputs']['Scenario']['Site']['CHP'].get("year_one_fuel_used_mmbtu") or 0 > 0:
            cannot_calc_total_emissions = True
            missing_emissions.append('CHP')
        elif data['outputs']['Scenario']['Site']['CHP'].get("year_one_fuel_used_mmbtu") or 0 == 0:
            data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_lb_CO2'] = 0
        
        data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_bau_lb_CO2'] = 0

        # Boiler emissions
        boiler_emmissions = data['inputs']['Scenario']['Site']['Boiler'].get('emissions_factor_lb_CO2_per_mmbtu')
        if boiler_emmissions is not None:
            data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_lb_CO2'] = \
                round(boiler_emmissions * (data['outputs']['Scenario']['Site']['Boiler'].get("year_one_boiler_fuel_consumption_mmbtu") or 0)\
                ,precision)
            
            data['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'] += \
                round(data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_lb_CO2'],precision)
            
            data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_bau_lb_CO2'] = \
                round(boiler_emmissions * \
                (data['outputs']['Scenario']['Site']['LoadProfileBoilerFuel'].get("annual_calculated_boiler_fuel_load_mmbtu_bau") or 0)\
                ,precision)

            data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'] += \
            round(data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_bau_lb_CO2'],precision)
        
        else:
            if data['outputs']['Scenario']['Site']['Boiler'].get("year_one_boiler_fuel_consumption_mmbtu") or 0 > 0:
                cannot_calc_total_emissions = True
                missing_emissions.append('Boiler')
            else:
                data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_lb_CO2'] = 0
            
            if data['outputs']['Scenario']['Site']['LoadProfileBoilerFuel'].get("annual_calculated_boiler_fuel_load_mmbtu_bau") or 0 > 0:
                cannot_calc_bau_total_emissions = True
                missing_emissions.append('Boiler')
            else:
                data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_bau_lb_CO2'] = 0


        if cannot_calc_total_emissions:
            data['outputs']['Scenario']['Site']['year_one_emissions_lb_CO2'] = None

        if cannot_calc_bau_total_emissions:
            data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_CO2'] = None
        
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
            data['messages']['warnings']['Emissions Calculation Warning'] = message

        return data
    '''

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
            ## TODO: Levelize profile using emissions_factor_series_CO2_pct_decrease 
        return self._emmissions_profile

# class EmissionsCalculator_NOx:

#     def __init__(self, latitude=None, longitude=None, **kwargs):
#         """
#         :param latitude: float
#         :param longitude: float
#         :param kwargs:
#         """
#         self._region_lookup = None
#         self.library_path = os.path.join('reo', 'src', 'data')
#         self.latitude = float(latitude) if latitude is not None else None
#         self.longitude = float(longitude) if longitude is not None else None
#         self._region_abbr = None
#         self._emmissions_profile = None
#         self._transmission_and_distribution_losses = None
#         self.meters_to_region = None
#         self.time_steps_per_hour = kwargs.get('time_steps_per_hour') or 1
#         proj102008 = pyproj.Proj("+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs")
#         self.project4326_to_102008 = partial(pyproj.transform,pyproj.Proj(init='epsg:4326'),proj102008)
    
#     @staticmethod
#     def add_to_data(data):

#         precision = 1
#         cannot_calc_total_emissions = False
#         cannot_calc_bau_total_emissions = False
#         missing_emissions = []

        
#         data['outputs']['Scenario']['Site']['year_one_emissions_lb_NOx'] = 0
#         data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_NOx'] = 0

#         hourly_emissions = np.array(data['inputs']['Scenario']['Site']['ElectricTariff'].get('emissions_factor_series_lb_NOx_per_kwh') or [])
#         from_utility_series = np.array(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_load_series_kw') \
#             or [0 for _ in range(8760 *self.time_steps_per_hour)]) + \
#             np.array(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_battery_series_kw') or \
#             [0 for _ in range(8760 * self.time_steps_per_hour)]) 

#         # If user supplies hourly NOx emissions rates
#         if hourly_emissions.shape[0] > 0:
#             # Year one NOx emissions from grid purchases (excludes exports)
#             data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_NOx'] = \
#             round((hourly_emissions * from_utility_series).sum(),precision)
            
#             # Add to total Year 1 NOx emissions
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_NOx'] += \
#             round(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_NOx'],precision)

#             # BAU calcs
#             loads_kw = np.array(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_to_load_series_bau_kw'] or [])
#             if len(loads_kw) == 0:
#                 loads_kw = 0
#             data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_NOx'] = \
#                 round((hourly_emissions * loads_kw).sum(),precision)
#             data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_NOx'] += \
#                 round(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_NOx'],precision)
        
#         # If user has not supplied NOx emissions rates
#         else:
#             if (sum(from_utility_series) > 0): ## why is this > 0?
#                 cannot_calc_total_emissions = True
#                 missing_emissions.append('ElectricTariff')
#             else:
#                 data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_NOx'] = 0

#             if (sum(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_load_bau_series_kw') or [0]) > 0):
#                 cannot_calc_bau_total_emissions = True
#                 missing_emissions.append('ElectricTariff')
#             else:
#                 data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_NOx'] = 0

#         # Generator emissions
#         generator_emmissions = data['inputs']['Scenario']['Site']['Generator'].get('emissions_factor_lb_NOx_per_gal')
#         if generator_emmissions is not None:
#             data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_NOx'] = \
#                 round(generator_emmissions * (data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal") or 0),precision)
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_NOx'] += \
#                 round(data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_NOx'],precision)
            
#             data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_NOx'] = \
#                 round(generator_emmissions *  (data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal_bau") or 0),precision)
#             data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_NOx'] += \
#                 round(data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_NOx'],precision)
                        
#         else:
#             if data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal") or 0 > 0:
#                 cannot_calc_total_emissions = True
#                 missing_emissions.append('Generator')
#             else:
#                 data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_NOx'] = 0

#             if data['outputs']['Scenario']['Site']['Generator'].get('fuel_used_gal_bau') or 0 > 0:
#                 cannot_calc_bau_total_emissions = True
#                 missing_emissions.append('Generator')
#             else:
#                 data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_NOx'] = 0
        
#         # CHP emissions
#         chp_emmissions = data['inputs']['Scenario']['Site']['CHP'].get('emissions_factor_lb_NOx_per_mmbtu')
#         if chp_emmissions is not None:
#             data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_lb_NOx'] = \
#                 round(chp_emmissions * (data['outputs']['Scenario']['Site']['CHP'].get("year_one_fuel_used_mmbtu") or 0),precision)
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_NOx'] += \
#                 round(data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_lb_NOx'],precision)
            
#         elif data['outputs']['Scenario']['Site']['CHP'].get("year_one_fuel_used_mmbtu") or 0 > 0:
#             cannot_calc_total_emissions = True
#             missing_emissions.append('CHP')
#         elif data['outputs']['Scenario']['Site']['CHP'].get("year_one_fuel_used_mmbtu") or 0 == 0:
#             data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_lb_NOx'] = 0
        
#         data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_bau_lb_NOx'] = 0

#         # Boiler emissions
#         boiler_emmissions = data['inputs']['Scenario']['Site']['Boiler'].get('emissions_factor_lb_NOx_per_mmbtu')
#         if boiler_emmissions is not None:
#             data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_lb_NOx'] = \
#                 round(boiler_emmissions * (data['outputs']['Scenario']['Site']['Boiler'].get("year_one_boiler_fuel_consumption_mmbtu") or 0)\
#                 ,precision)
            
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_NOx'] += \
#                 round(data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_lb_NOx'],precision)
            
#             data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_bau_lb_NOx'] = \
#                 round(boiler_emmissions * \
#                 (data['outputs']['Scenario']['Site']['LoadProfileBoilerFuel'].get("annual_calculated_boiler_fuel_load_mmbtu_bau") or 0)\
#                 ,precision)

#             data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_NOx'] += \
#             round(data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_bau_lb_NOx'],precision)
        
#         else:
#             if data['outputs']['Scenario']['Site']['Boiler'].get("year_one_boiler_fuel_consumption_mmbtu") or 0 > 0:
#                 cannot_calc_total_emissions = True
#                 missing_emissions.append('Boiler')
#             else:
#                 data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_lb_NOx'] = 0
            
#             if data['outputs']['Scenario']['Site']['LoadProfileBoilerFuel'].get("annual_calculated_boiler_fuel_load_mmbtu_bau") or 0 > 0:
#                 cannot_calc_bau_total_emissions = True
#                 missing_emissions.append('Boiler')
#             else:
#                 data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_bau_lb_NOx'] = 0


#         if cannot_calc_total_emissions:
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_NOx'] = None

#         if cannot_calc_bau_total_emissions:
#             data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_NOx'] = None
        
#         if cannot_calc_bau_total_emissions or cannot_calc_total_emissions:
            
#             message  = 'Could not calculate Site level emissions'
#             if cannot_calc_total_emissions:
#                 message += ' for optimized results'
#             if cannot_calc_bau_total_emissions:
#                 if cannot_calc_total_emissions:
#                     message += ' or'
#                 message += ' for BAU case'
            
#             message += '. Missing an emission factor for the following: {}'.format(','.join(set(missing_emissions)))

#             if 'messages' not in data.keys():
#                 data['messages'] = {"warnings":{}}
#             if 'warnings' not in data['messages'].keys():
#                 data['messages']["warnings"] = {}
#             data['messages']['warnings']['Emissions Calculation Warning'] = message

#         return data

#     @property
#     def region(self):
#         lookup = {  'AK':'Alaska',
#                     'CA':'California',
#                     'EMW':'Great Lakes / Atlantic',
#                     'NE': 'Northeast',
#                     'NW':'Northwest',
#                     'RM':'Rocky Mountains',
#                     'SC':'Lower Midwest',
#                     'SE': 'Southeast',
#                     'SW':'Southwest',
#                     'TX':'Texas',
#                     'WMW':'Upper Midwest',
#                     'HI':'Hawaii (except Oahu)',
#                     'HI-Oahu':'Hawaii (Oahu)' }
        
#         if self.region_abbr is not None:
#             return lookup[self.region_abbr]
#         return None
    
#     @property
#     def region_abbr(self):
#         if self._region_abbr is None:
#             gdf = gpd.read_file(os.path.join(self.library_path,'avert_4326.shp'))

#             gdf_query = gdf[gdf.geometry.intersects(g.Point(self.longitude, self.latitude))]
#             if not gdf_query.empty:
#                 self.meters_to_region = 0
#                 self._region_abbr = gdf_query.AVERT.values[0]
                
#             if self._region_abbr is None:
#                 gdf = gpd.read_file(os.path.join(self.library_path,'avert_102008.shp'))
#                 try:
#                     lookup = transform(self.project4326_to_102008, g.Point(self.longitude, self.latitude))
#                 except:
#                     raise AttributeError("Could not look up AVERT emissions region from point ({},{}). Location is\
#                         likely invalid or well outside continental US, AK and HI".format(self.longitude, self.latitude))
#                 distances_meter = gdf.geometry.apply(lambda x : x.distance(lookup)).values
#                 min_idx = list(distances_meter).index(min(distances_meter))
#                 self._region_abbr = gdf.loc[min_idx,'AVERT']
#                 self.meters_to_region = int(round(min(distances_meter)))
#                 if self.meters_to_region > 8046:
#                     raise AttributeError('Your site location ({},{}) is more than 5 miles from the '
#                         'nearest emission region. Cannot calculate emissions.'.format(self.longitude, self.latitude))
#         return self._region_abbr
    
#     @property
#     def emissions_series(self):
#         if self._emmissions_profile is None:
#             df = pd.read_csv(os.path.join(self.library_path,'AVERT_hourly_emissions_NOx.csv'))
#             if self.region_abbr in df.columns:
#                 self._emmissions_profile = list(df[self.region_abbr].round(3).values)
#                 if self.time_steps_per_hour > 1:
#                     self._emmissions_profile = list(np.concatenate([[i] * self.time_steps_per_hour for i in self._emmissions_profile]))
#             else:
#                 raise AttributeError("NOx Emissions error. Cannnot find hourly emmissions for region {} ({},{}) \
#                     ".format(self.region, self.latitude,self.longitude))
#         return self._emmissions_profile


# class EmissionsCalculator_SO2:

#     def __init__(self, latitude=None, longitude=None, **kwargs):
#         """
#         :param latitude: float
#         :param longitude: float
#         :param kwargs:
#         """
#         self._region_lookup = None
#         self.library_path = os.path.join('reo', 'src', 'data')
#         self.latitude = float(latitude) if latitude is not None else None
#         self.longitude = float(longitude) if longitude is not None else None
#         self._region_abbr = None
#         self._emmissions_profile = None
#         self._transmission_and_distribution_losses = None
#         self.meters_to_region = None
#         self.time_steps_per_hour = kwargs.get('time_steps_per_hour') or 1
#         proj102008 = pyproj.Proj("+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs")
#         self.project4326_to_102008 = partial(pyproj.transform,pyproj.Proj(init='epsg:4326'),proj102008)
    
#     @staticmethod
#     def add_to_data(data):

#         precision = 1
#         cannot_calc_total_emissions = False
#         cannot_calc_bau_total_emissions = False
#         missing_emissions = []

        
#         data['outputs']['Scenario']['Site']['year_one_emissions_lb_SO2'] = 0
#         data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_SO2'] = 0

#         hourly_emissions = np.array(data['inputs']['Scenario']['Site']['ElectricTariff'].get('emissions_factor_series_lb_SO2_per_kwh') or [])
#         from_utility_series = np.array(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_load_series_kw') \
#             or [0 for _ in range(8760 *self.time_steps_per_hour)]) + \
#             np.array(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_battery_series_kw') or \
#             [0 for _ in range(8760 * self.time_steps_per_hour)]) 

#         # If user supplies hourly SO2 emissions rates
#         if hourly_emissions.shape[0] > 0:
#             # Year one SO2 emissions from grid purchases (excludes exports)
#             data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_SO2'] = \
#             round((hourly_emissions * from_utility_series).sum(),precision)
            
#             # Add to total Year 1 SO2 emissions
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_SO2'] += \
#             round(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_SO2'],precision)

#             # BAU calcs
#             loads_kw = np.array(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_to_load_series_bau_kw'] or [])
#             if len(loads_kw) == 0:
#                 loads_kw = 0
#             data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_SO2'] = \
#                 round((hourly_emissions * loads_kw).sum(),precision)
#             data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_SO2'] += \
#                 round(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_SO2'],precision)
        
#         # If user has not supplied SO2 emissions rates
#         else:
#             if (sum(from_utility_series) > 0): ## why is this > 0?
#                 cannot_calc_total_emissions = True
#                 missing_emissions.append('ElectricTariff')
#             else:
#                 data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_SO2'] = 0

#             if (sum(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_load_bau_series_kw') or [0]) > 0):
#                 cannot_calc_bau_total_emissions = True
#                 missing_emissions.append('ElectricTariff')
#             else:
#                 data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_SO2'] = 0

#         # Generator emissions
#         generator_emmissions = data['inputs']['Scenario']['Site']['Generator'].get('emissions_factor_lb_SO2_per_gal')
#         if generator_emmissions is not None:
#             data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_SO2'] = \
#                 round(generator_emmissions * (data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal") or 0),precision)
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_SO2'] += \
#                 round(data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_SO2'],precision)
            
#             data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_SO2'] = \
#                 round(generator_emmissions *  (data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal_bau") or 0),precision)
#             data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_SO2'] += \
#                 round(data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_SO2'],precision)
                        
#         else:
#             if data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal") or 0 > 0:
#                 cannot_calc_total_emissions = True
#                 missing_emissions.append('Generator')
#             else:
#                 data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_SO2'] = 0

#             if data['outputs']['Scenario']['Site']['Generator'].get('fuel_used_gal_bau') or 0 > 0:
#                 cannot_calc_bau_total_emissions = True
#                 missing_emissions.append('Generator')
#             else:
#                 data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_SO2'] = 0
        
#         # CHP emissions
#         chp_emmissions = data['inputs']['Scenario']['Site']['CHP'].get('emissions_factor_lb_SO2_per_mmbtu')
#         if chp_emmissions is not None:
#             data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_lb_SO2'] = \
#                 round(chp_emmissions * (data['outputs']['Scenario']['Site']['CHP'].get("year_one_fuel_used_mmbtu") or 0),precision)
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_SO2'] += \
#                 round(data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_lb_SO2'],precision)
            
#         elif data['outputs']['Scenario']['Site']['CHP'].get("year_one_fuel_used_mmbtu") or 0 > 0:
#             cannot_calc_total_emissions = True
#             missing_emissions.append('CHP')
#         elif data['outputs']['Scenario']['Site']['CHP'].get("year_one_fuel_used_mmbtu") or 0 == 0:
#             data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_lb_SO2'] = 0
        
#         data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_bau_lb_SO2'] = 0

#         # Boiler emissions
#         boiler_emmissions = data['inputs']['Scenario']['Site']['Boiler'].get('emissions_factor_lb_SO2_per_mmbtu')
#         if boiler_emmissions is not None:
#             data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_lb_SO2'] = \
#                 round(boiler_emmissions * (data['outputs']['Scenario']['Site']['Boiler'].get("year_one_boiler_fuel_consumption_mmbtu") or 0)\
#                 ,precision)
            
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_SO2'] += \
#                 round(data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_lb_SO2'],precision)
            
#             data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_bau_lb_SO2'] = \
#                 round(boiler_emmissions * \
#                 (data['outputs']['Scenario']['Site']['LoadProfileBoilerFuel'].get("annual_calculated_boiler_fuel_load_mmbtu_bau") or 0)\
#                 ,precision)

#             data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_SO2'] += \
#             round(data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_bau_lb_SO2'],precision)
        
#         else:
#             if data['outputs']['Scenario']['Site']['Boiler'].get("year_one_boiler_fuel_consumption_mmbtu") or 0 > 0:
#                 cannot_calc_total_emissions = True
#                 missing_emissions.append('Boiler')
#             else:
#                 data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_lb_SO2'] = 0
            
#             if data['outputs']['Scenario']['Site']['LoadProfileBoilerFuel'].get("annual_calculated_boiler_fuel_load_mmbtu_bau") or 0 > 0:
#                 cannot_calc_bau_total_emissions = True
#                 missing_emissions.append('Boiler')
#             else:
#                 data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_bau_lb_SO2'] = 0


#         if cannot_calc_total_emissions:
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_SO2'] = None

#         if cannot_calc_bau_total_emissions:
#             data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_SO2'] = None
        
#         if cannot_calc_bau_total_emissions or cannot_calc_total_emissions:
            
#             message  = 'Could not calculate Site level emissions'
#             if cannot_calc_total_emissions:
#                 message += ' for optimized results'
#             if cannot_calc_bau_total_emissions:
#                 if cannot_calc_total_emissions:
#                     message += ' or'
#                 message += ' for BAU case'
            
#             message += '. Missing an emission factor for the following: {}'.format(','.join(set(missing_emissions)))

#             if 'messages' not in data.keys():
#                 data['messages'] = {"warnings":{}}
#             if 'warnings' not in data['messages'].keys():
#                 data['messages']["warnings"] = {}
#             data['messages']['warnings']['Emissions Calculation Warning'] = message

#         return data

#     @property
#     def region(self):
#         lookup = {  'AK':'Alaska',
#                     'CA':'California',
#                     'EMW':'Great Lakes / Atlantic',
#                     'NE': 'Northeast',
#                     'NW':'Northwest',
#                     'RM':'Rocky Mountains',
#                     'SC':'Lower Midwest',
#                     'SE': 'Southeast',
#                     'SW':'Southwest',
#                     'TX':'Texas',
#                     'WMW':'Upper Midwest',
#                     'HI':'Hawaii (except Oahu)',
#                     'HI-Oahu':'Hawaii (Oahu)' }
        
#         if self.region_abbr is not None:
#             return lookup[self.region_abbr]
#         return None
    
#     @property
#     def region_abbr(self):
#         if self._region_abbr is None:
#             gdf = gpd.read_file(os.path.join(self.library_path,'avert_4326.shp'))

#             gdf_query = gdf[gdf.geometry.intersects(g.Point(self.longitude, self.latitude))]
#             if not gdf_query.empty:
#                 self.meters_to_region = 0
#                 self._region_abbr = gdf_query.AVERT.values[0]
                
#             if self._region_abbr is None:
#                 gdf = gpd.read_file(os.path.join(self.library_path,'avert_102008.shp'))
#                 try:
#                     lookup = transform(self.project4326_to_102008, g.Point(self.longitude, self.latitude))
#                 except:
#                     raise AttributeError("Could not look up AVERT emissions region from point ({},{}). Location is\
#                         likely invalid or well outside continental US, AK and HI".format(self.longitude, self.latitude))
#                 distances_meter = gdf.geometry.apply(lambda x : x.distance(lookup)).values
#                 min_idx = list(distances_meter).index(min(distances_meter))
#                 self._region_abbr = gdf.loc[min_idx,'AVERT']
#                 self.meters_to_region = int(round(min(distances_meter)))
#                 if self.meters_to_region > 8046:
#                     raise AttributeError('Your site location ({},{}) is more than 5 miles from the '
#                         'nearest emission region. Cannot calculate emissions.'.format(self.longitude, self.latitude))
#         return self._region_abbr
    
#     @property
#     def emissions_series(self):
#         if self._emmissions_profile is None:
#             df = pd.read_csv(os.path.join(self.library_path,'AVERT_hourly_emissions_SO2.csv'))
#             if self.region_abbr in df.columns:
#                 self._emmissions_profile = list(df[self.region_abbr].round(3).values)
#                 if self.time_steps_per_hour > 1:
#                     self._emmissions_profile = list(np.concatenate([[i] * self.time_steps_per_hour for i in self._emmissions_profile]))
#             else:
#                 raise AttributeError("SO2 Emissions error. Cannnot find hourly emmissions for region {} ({},{}) \
#                     ".format(self.region, self.latitude,self.longitude))
#         return self._emmissions_profile

# class EmissionsCalculator_PM:

#     def __init__(self, latitude=None, longitude=None, **kwargs):
#         """
#         :param latitude: float
#         :param longitude: float
#         :param kwargs:
#         """
#         self._region_lookup = None
#         self.library_path = os.path.join('reo', 'src', 'data')
#         self.latitude = float(latitude) if latitude is not None else None
#         self.longitude = float(longitude) if longitude is not None else None
#         self._region_abbr = None
#         self._emmissions_profile = None
#         self._transmission_and_distribution_losses = None
#         self.meters_to_region = None
#         self.time_steps_per_hour = kwargs.get('time_steps_per_hour') or 1
#         proj102008 = pyproj.Proj("+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs")
#         self.project4326_to_102008 = partial(pyproj.transform,pyproj.Proj(init='epsg:4326'),proj102008)
    
#     @staticmethod
#     def add_to_data(data):

#         precision = 1
#         cannot_calc_total_emissions = False
#         cannot_calc_bau_total_emissions = False
#         missing_emissions = []

        
#         data['outputs']['Scenario']['Site']['year_one_emissions_lb_PM'] = 0
#         data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_PM'] = 0

#         hourly_emissions = np.array(data['inputs']['Scenario']['Site']['ElectricTariff'].get('emissions_factor_series_lb_PM_per_kwh') or [])
#         from_utility_series = np.array(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_load_series_kw') \
#             or [0 for _ in range(8760 *self.time_steps_per_hour)]) + \
#             np.array(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_battery_series_kw') or \
#             [0 for _ in range(8760 * self.time_steps_per_hour)]) 

#         # If user supplies hourly PM emissions rates
#         if hourly_emissions.shape[0] > 0:
#             # Year one PM emissions from grid purchases (excludes exports)
#             data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_PM'] = \
#             round((hourly_emissions * from_utility_series).sum(),precision)
            
#             # Add to total Year 1 PM emissions
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_PM'] += \
#             round(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_PM'],precision)

#             # BAU calcs
#             loads_kw = np.array(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_to_load_series_bau_kw'] or [])
#             if len(loads_kw) == 0:
#                 loads_kw = 0
#             data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_PM'] = \
#                 round((hourly_emissions * loads_kw).sum(),precision)
#             data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_PM'] += \
#                 round(data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_PM'],precision)
        
#         # If user has not supplied PM emissions rates
#         else:
#             if (sum(from_utility_series) > 0): ## why is this > 0?
#                 cannot_calc_total_emissions = True
#                 missing_emissions.append('ElectricTariff')
#             else:
#                 data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_lb_PM'] = 0

#             if (sum(data['outputs']['Scenario']['Site']['ElectricTariff'].get('year_one_to_load_bau_series_kw') or [0]) > 0):
#                 cannot_calc_bau_total_emissions = True
#                 missing_emissions.append('ElectricTariff')
#             else:
#                 data['outputs']['Scenario']['Site']['ElectricTariff']['year_one_emissions_bau_lb_PM'] = 0

#         # Generator emissions
#         generator_emmissions = data['inputs']['Scenario']['Site']['Generator'].get('emissions_factor_lb_PM_per_gal')
#         if generator_emmissions is not None:
#             data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_PM'] = \
#                 round(generator_emmissions * (data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal") or 0),precision)
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_PM'] += \
#                 round(data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_PM'],precision)
            
#             data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_PM'] = \
#                 round(generator_emmissions *  (data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal_bau") or 0),precision)
#             data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_PM'] += \
#                 round(data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_PM'],precision)
                        
#         else:
#             if data['outputs']['Scenario']['Site']['Generator'].get("fuel_used_gal") or 0 > 0:
#                 cannot_calc_total_emissions = True
#                 missing_emissions.append('Generator')
#             else:
#                 data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_lb_PM'] = 0

#             if data['outputs']['Scenario']['Site']['Generator'].get('fuel_used_gal_bau') or 0 > 0:
#                 cannot_calc_bau_total_emissions = True
#                 missing_emissions.append('Generator')
#             else:
#                 data['outputs']['Scenario']['Site']['Generator']['year_one_emissions_bau_lb_PM'] = 0
        
#         # CHP emissions
#         chp_emmissions = data['inputs']['Scenario']['Site']['CHP'].get('emissions_factor_lb_PM_per_mmbtu')
#         if chp_emmissions is not None:
#             data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_lb_PM'] = \
#                 round(chp_emmissions * (data['outputs']['Scenario']['Site']['CHP'].get("year_one_fuel_used_mmbtu") or 0),precision)
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_PM'] += \
#                 round(data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_lb_PM'],precision)
            
#         elif data['outputs']['Scenario']['Site']['CHP'].get("year_one_fuel_used_mmbtu") or 0 > 0:
#             cannot_calc_total_emissions = True
#             missing_emissions.append('CHP')
#         elif data['outputs']['Scenario']['Site']['CHP'].get("year_one_fuel_used_mmbtu") or 0 == 0:
#             data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_lb_PM'] = 0
        
#         data['outputs']['Scenario']['Site']['CHP']['year_one_emissions_bau_lb_PM'] = 0

#         # Boiler emissions
#         boiler_emmissions = data['inputs']['Scenario']['Site']['Boiler'].get('emissions_factor_lb_PM_per_mmbtu')
#         if boiler_emmissions is not None:
#             data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_lb_PM'] = \
#                 round(boiler_emmissions * (data['outputs']['Scenario']['Site']['Boiler'].get("year_one_boiler_fuel_consumption_mmbtu") or 0)\
#                 ,precision)
            
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_PM'] += \
#                 round(data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_lb_PM'],precision)
            
#             data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_bau_lb_PM'] = \
#                 round(boiler_emmissions * \
#                 (data['outputs']['Scenario']['Site']['LoadProfileBoilerFuel'].get("annual_calculated_boiler_fuel_load_mmbtu_bau") or 0)\
#                 ,precision)

#             data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_PM'] += \
#             round(data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_bau_lb_PM'],precision)
        
#         else:
#             if data['outputs']['Scenario']['Site']['Boiler'].get("year_one_boiler_fuel_consumption_mmbtu") or 0 > 0:
#                 cannot_calc_total_emissions = True
#                 missing_emissions.append('Boiler')
#             else:
#                 data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_lb_PM'] = 0
            
#             if data['outputs']['Scenario']['Site']['LoadProfileBoilerFuel'].get("annual_calculated_boiler_fuel_load_mmbtu_bau") or 0 > 0:
#                 cannot_calc_bau_total_emissions = True
#                 missing_emissions.append('Boiler')
#             else:
#                 data['outputs']['Scenario']['Site']['Boiler']['year_one_emissions_bau_lb_PM'] = 0


#         if cannot_calc_total_emissions:
#             data['outputs']['Scenario']['Site']['year_one_emissions_lb_PM'] = None

#         if cannot_calc_bau_total_emissions:
#             data['outputs']['Scenario']['Site']['year_one_emissions_bau_lb_PM'] = None
        
#         if cannot_calc_bau_total_emissions or cannot_calc_total_emissions:
            
#             message  = 'Could not calculate Site level emissions'
#             if cannot_calc_total_emissions:
#                 message += ' for optimized results'
#             if cannot_calc_bau_total_emissions:
#                 if cannot_calc_total_emissions:
#                     message += ' or'
#                 message += ' for BAU case'
            
#             message += '. Missing an emission factor for the following: {}'.format(','.join(set(missing_emissions)))

#             if 'messages' not in data.keys():
#                 data['messages'] = {"warnings":{}}
#             if 'warnings' not in data['messages'].keys():
#                 data['messages']["warnings"] = {}
#             data['messages']['warnings']['Emissions Calculation Warning'] = message

#         return data

#     @property
#     def region(self):
#         lookup = {  'AK':'Alaska',
#                     'CA':'California',
#                     'EMW':'Great Lakes / Atlantic',
#                     'NE': 'Northeast',
#                     'NW':'Northwest',
#                     'RM':'Rocky Mountains',
#                     'SC':'Lower Midwest',
#                     'SE': 'Southeast',
#                     'SW':'Southwest',
#                     'TX':'Texas',
#                     'WMW':'Upper Midwest',
#                     'HI':'Hawaii (except Oahu)',
#                     'HI-Oahu':'Hawaii (Oahu)' }
        
#         if self.region_abbr is not None:
#             return lookup[self.region_abbr]
#         return None
    
#     @property
#     def region_abbr(self):
#         if self._region_abbr is None:
#             gdf = gpd.read_file(os.path.join(self.library_path,'avert_4326.shp'))

#             gdf_query = gdf[gdf.geometry.intersects(g.Point(self.longitude, self.latitude))]
#             if not gdf_query.empty:
#                 self.meters_to_region = 0
#                 self._region_abbr = gdf_query.AVERT.values[0]
                
#             if self._region_abbr is None:
#                 gdf = gpd.read_file(os.path.join(self.library_path,'avert_102008.shp'))
#                 try:
#                     lookup = transform(self.project4326_to_102008, g.Point(self.longitude, self.latitude))
#                 except:
#                     raise AttributeError("Could not look up AVERT emissions region from point ({},{}). Location is\
#                         likely invalid or well outside continental US, AK and HI".format(self.longitude, self.latitude))
#                 distances_meter = gdf.geometry.apply(lambda x : x.distance(lookup)).values
#                 min_idx = list(distances_meter).index(min(distances_meter))
#                 self._region_abbr = gdf.loc[min_idx,'AVERT']
#                 self.meters_to_region = int(round(min(distances_meter)))
#                 if self.meters_to_region > 8046:
#                     raise AttributeError('Your site location ({},{}) is more than 5 miles from the '
#                         'nearest emission region. Cannot calculate emissions.'.format(self.longitude, self.latitude))
#         return self._region_abbr
    
#     @property
#     def emissions_series(self):
#         if self._emmissions_profile is None:
#             df = pd.read_csv(os.path.join(self.library_path,'AVERT_hourly_emissions_PM.csv'))
#             if self.region_abbr in df.columns:
#                 self._emmissions_profile = list(df[self.region_abbr].round(3).values)
#                 if self.time_steps_per_hour > 1:
#                     self._emmissions_profile = list(np.concatenate([[i] * self.time_steps_per_hour for i in self._emmissions_profile]))
#             else:
#                 raise AttributeError("PM Emissions error. Cannnot find hourly emmissions for region {} ({},{}) \
#                     ".format(self.region, self.latitude,self.longitude))
#         return self._emmissions_profile
