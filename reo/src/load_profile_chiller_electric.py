from reo.src.load_profile import BuiltInProfile
import pandas as pd
import numpy as np
from datetime import datetime


class LoadProfileChillerElectric(object):
    """
    Contains information relevant to construct a thermal load,
    Presently just takes 8760, so not much to do
    """
    
    annual_loads = {}

    builtin_profile_prefix = "Cooling8760_fraction_"
    
    def __init__(self, dfm, lp, annual_fraction=None, monthly_fraction=None, loads_fraction=None, latitude=None, longitude=None, time_steps_per_hour=None, doe_reference_name=None, nearest_city=None, year=None, percent_share_list=None, **kwargs):
        self.time_steps_per_hour = time_steps_per_hour
        if annual_fraction is not None:
            self.load_list = [annual_fraction * kw for kw in lp.unmodified_load_list]

        elif monthly_fraction is not None:
            month_series = pd.date_range(datetime(lp.year,1,1), datetime(lp.year+1,1,1), periods=8760*time_steps_per_hour)
            self.load_list = [lp.unmodified_load_list[i] * monthly_fraction[month-1]  for i, month in enumerate(month_series.month)] 
        
        elif loads_fraction is not None:
            self.load_list = list(np.array(loads_fraction) * np.array(lp.unmodified_load_list))

        elif doe_reference_name:
                
            if len(doe_reference_name) == 1:

                chiller_profile = BuiltInProfile(
                    self.annual_loads,
                    self.builtin_profile_prefix,
                    latitude=latitude,
                    longitude=longitude,
                    doe_reference_name=doe_reference_name[0],
                    nearest_city=nearest_city,
                    year=year,
                    annual_energy=1,
                    monthly_totals_energy=None,
                    **kwargs)                
                
                self.load_list = list(np.array(chiller_profile.built_in_profile) * np.array(lp.unmodified_load_list))

            else:
                self.percent_share_list = percent_share_list
                combine_loadlist = []
                for i in range(len(doe_reference_name)):
                    chiller_profile = BuiltInProfile(
                        self.annual_loads,
                        self.builtin_profile_prefix,
                        latitude=latitude,
                        longitude=longitude,
                        doe_reference_name=doe_reference_name[i],
                        nearest_city=nearest_city,
                        year=year,
                        annual_energy=1,
                        monthly_totals_energy=None,
                        **kwargs)

                    annual_electric = None
                    annual_electric_list = lp.annual_kwh_list 
                    if annual_electric_list is not None:
                        annual_electric = annual_electric_list[i]
                    
                    electric_profile = LoadProfile(dfm=None, latitude=latitude, 
                        longitude=longitude, doe_reference_name=doe_reference_name[i],
                        annual_kwh=annual_electric, critical_load_pct=0)
                    
                    percent_share = self.percent_share_list[i]
                    
                    if time_steps_per_hour > 1:
                        fractions_of_load = np.concatenate([[x] * time_steps_per_hour for x in chiller_profile.built_in_profile])
                    else:
                        fractions_of_load = chiller_profile.built_in_profile

                    # appending the weighted load at every timestep, for making hybrid loadlist
                    combine_loadlist.append(list(np.array(fractions_of_load) * np.array(electric_profile) * (percent_share/100.0)))


                hybrid_loadlist = list(np.sum(np.array(combine_loadlist), 0))
                
                self.load_list = copy.copy(hybrid_loadlist)

        self.annual_kwh = sum(self.load_list)
        dfm.add_load_chiller_electric(self)
