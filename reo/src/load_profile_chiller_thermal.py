from reo.src.load_profile import BuiltInProfile
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from reo.utilities import TONHOUR_TO_KWHT


class LoadProfileChillerThermal(BuiltInProfile):
    """
    Chiller Load Profiles based on CRB defined load shapes or user-defined input
    """
    
    with open(os.path.join(BuiltInProfile.library_path, 'reference_cooling_tonhour.json'), 'r') as f:
        annual_loads = json.loads(f.read())

    builtin_profile_prefix = "Cooling8760_norm_"

    electric_chiller_cop_defaults = {   "convert_elec_to_thermal": 4.55,
                                            "less_than_100_tons": 4.40,
                                            "greater_than_100_tons": 4.69}
    
    def __init__(self, dfm=None, total_electric_load_list=[], latitude=None, longitude=None, nearest_city=None,
                        time_steps_per_hour=None, year=None, chiller_cop=None, max_thermal_factor_on_peak_load=None, **kwargs):
        """
        :param dfm: (object) data_manager to which this load object will be added
        :param total_electric_load_list: (array) electric LoadProfile object resulting from parsed inputs
        :param latitude: (float) site latitude
        :param longitude: (float) site longitude
        :param nearest_city: (str) site nearest_city
        :param time_steps_per_hour: (int) simulation time resolution
        :param year: (int) electric LoadProfile year
        :param chiller_cop: (float or int) Coefficient of Performance for Chiller
        :param max_thermal_factor_on_peak_load: (float or int) maximum thermal factor on peak load for the Chiller
        :param kwargs: (dict) Chiller specific inputs as defined in reo/nested_inputs
        """
        
        # Default electric_load_list to None, used later to see if we need to covert kWh to kWht
        electric_load_list = None
        
        # Use highest resultion/quality input first
        if kwargs.get('loads_ton') is not None:
            self.load_list = [i*TONHOUR_TO_KWHT for i in kwargs['loads_ton']]
        
        # DOE Reference building profile are used if there is a reference name provided
        elif kwargs.get('doe_reference_name'):
            doe_reference_name = kwargs.get('doe_reference_name') or []
            combine_loadlist = []
            for i in range(len(doe_reference_name)):
                # Monthly loads can only be used to scale a non-hybrid profile
                kwargs['monthly_totals_energy'] = kwargs.get("monthly_tonhour")
                if len(doe_reference_name)>1:
                    kwargs['monthly_totals_energy'] = None
                
                kwargs['annual_energy'] = None
                # Annual loads are used in place of percent shares if provided
                if (kwargs.get("annual_tonhour") or None) is not None:
                    kwargs['annual_energy'] = kwargs["annual_tonhour"]
                
                kwargs['annual_loads'] = self.annual_loads
                kwargs['builtin_profile_prefix'] = self.builtin_profile_prefix
                kwargs['latitude'] = latitude
                kwargs['longitude'] = longitude
                kwargs['doe_reference_name'] = doe_reference_name[i]
                kwargs['nearest_city'] = nearest_city
                kwargs['time_steps_per_hour'] = time_steps_per_hour
                kwargs['year'] = year
                super(LoadProfileChillerThermal, self).__init__(**kwargs)
                if time_steps_per_hour > 1:
                    partial_load_list = np.concatenate([[x] * time_steps_per_hour \
                                                            for x in self.built_in_profile])
                else:
                    partial_load_list = self.built_in_profile
                combine_loadlist.append(list(partial_load_list))

            # In the case where the user supplies a list of doe_reference_names and percent shares
            # for consistency we want to act as if we had scaled the partial load to the total site 
            # load which was unknown at the start of the loop above. This scalar makes it such that
            # when the percent shares are later applied that the total site load will be the sum
            # of the default annual loads for this location
            if (len(doe_reference_name) > 1) and kwargs['annual_energy'] is None:
                total_site_load = sum([sum(l) for l in combine_loadlist])
                for i, load in enumerate(combine_loadlist):
                    actual_percent_of_site_load = sum(load)/total_site_load
                    scalar = 1.0 / actual_percent_of_site_load
                    combine_loadlist[i] = list(np.array(load)* scalar)
            
            #Apply the percent share of annual load to each partial load
            if (len(doe_reference_name) > 1):
                for i, load in enumerate(combine_loadlist):
                    combine_loadlist[i] = list(np.array(load) * (kwargs.get("percent_share")[i]/100.0))

            # Aggregate total hybrid load
            hybrid_loadlist = list(np.sum(np.array(combine_loadlist), 0))
            #load_list is always expected to be in units of kWt
            self.load_list = [i*TONHOUR_TO_KWHT for i in hybrid_loadlist]
        
        # If no doe_reference_name or loads_ton provided, scale by a fraction of electric load
        elif kwargs.get('loads_fraction') is not None:
            electric_load_list = list(np.array(kwargs['loads_fraction']) * np.array(total_electric_load_list))

        elif kwargs.get('monthly_fraction') is not None:
            month_series = pd.date_range(datetime(year,1,1), datetime(year+1,1,1), periods=8760*time_steps_per_hour)
            electric_load_list = [total_electric_load_list[i] * kwargs['monthly_fraction'][month-1] \
                                     for i, month in enumerate(month_series.month)] 

        elif kwargs.get('annual_fraction') is not None:
            electric_load_list = [kwargs['annual_fraction'] * kw for kw in total_electric_load_list]
        
        #Calculate COP based on kwth load or kw load (if not user-entered) 
        self.chiller_cop = kwargs.get('chiller_cop')
        # Update COP based on estimated max chiller load
        if self.chiller_cop is None:
            if electric_load_list is None:
                max_cooling_load_tons = np.array(self.load_list).max() / TONHOUR_TO_KWHT
            else:
                max_cooling_load_tons = max(electric_load_list) / TONHOUR_TO_KWHT * \
                                    self.electric_chiller_cop_defaults["convert_elec_to_thermal"]
            estimated_max_chiller_thermal_capacity_tons = max_cooling_load_tons * max_thermal_factor_on_peak_load
            if estimated_max_chiller_thermal_capacity_tons < 100.0:
                self.chiller_cop = self.electric_chiller_cop_defaults["less_than_100_tons"]
            else:
                self.chiller_cop = self.electric_chiller_cop_defaults["greater_than_100_tons"]
        
        # load_list is always expected to be in units of kWth
        if electric_load_list is not None:
            self.load_list = [i*self.chiller_cop for i in electric_load_list]
        
        self.annual_kwht = sum(self.load_list)
        if dfm is not None:
            dfm.add_load_chiller_thermal(self)
