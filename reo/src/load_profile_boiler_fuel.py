from reo.src.load_profile import BuiltInProfile
import json
import os
import copy
import numpy as np


class LoadProfileBoilerFuel(object):
    """
    Contains information relevant to construct a thermal load,
    Presently just takes 8760, so not much to do
    """
    with open(os.path.join(BuiltInProfile.library_path, 'reference_heating_mmbtu.json'), 'r') as f:
        annual_loads = json.loads(f.read())

    builtin_profile_prefix = "Heating8760_norm_"
    
    def __init__(self, dfm=None, latitude = None, longitude = None, time_steps_per_hour = None, loads_mmbtu_per_hour = [], doe_reference_name = None, nearest_city = None, year = None, percent_share_list = None, **kwargs):
        self.time_steps_per_hour = time_steps_per_hour
        self.nearest_city = nearest_city
        self.doe_reference_name = doe_reference_name
        if loads_mmbtu_per_hour:
            self.load_list = loads_mmbtu_per_hour
            self.annual_mmbtu = sum(self.load_list)

        else:  # building type and (annual_mmbtu OR monthly_mmbtu) defined by user

            if len(doe_reference_name) == 1:
                if len(kwargs.get('annual_mmbtu') or []) == 1:
                    kwargs['annual_mmbtu'] = kwargs['annual_mmbtu'][0]
                boiler_profile = BuiltInProfile(
                    self.annual_loads,
                    self.builtin_profile_prefix,
                    latitude=latitude,
                    longitude=longitude,
                    doe_reference_name=doe_reference_name[0],
                    nearest_city=nearest_city,
                    year=year,
                    annual_energy=kwargs.get('annual_mmbtu'),
                    monthly_totals_energy=kwargs.get('monthly_mmbtu'),
                    **kwargs)                
                
                if time_steps_per_hour > 1:
                    self.load_list = np.concatenate([float(x)/time_steps_per_hour for x in boiler_profile.built_in_profile])
                else:
                    self.load_list = boiler_profile.built_in_profile
            
            else:
                self.annual_mmbtu_list = kwargs.get("annual_mmbtu")
                self.percent_share_list = percent_share_list
                combine_loadlist = []
                for i in range(len(doe_reference_name)):
                    
                    annual_energy = None
                    if self.annual_mmbtu_list not in [None, []]:
                        annual_energy = self.annual_mmbtu_list[i]

                    boiler_profile = BuiltInProfile(
                        self.annual_loads,
                        self.builtin_profile_prefix,
                        latitude=latitude,
                        longitude=longitude,
                        doe_reference_name=doe_reference_name[i],
                        nearest_city=nearest_city,
                        year=year,
                        annual_energy=annual_energy)
                    
                    percent_share = self.percent_share_list[i]
                    
                    if time_steps_per_hour > 1:
                        self.load_list = np.concatenate([[x] * time_steps_per_hour for x in boiler_profile.built_in_profile])
                    else:
                        self.load_list = boiler_profile.built_in_profile

                    # appending the weighted load at every timestep, for making hybrid loadlist
                    combine_loadlist.append(list(np.array(boiler_profile) * (percent_share/100.0)))

                hybrid_loadlist = list(np.sum(np.array(combine_loadlist), 0))
                self.load_list = copy.copy(hybrid_loadlist)
            self.annual_mmbtu = sum(self.load_list)

        if dfm is not None:
            dfm.add_load_boiler_fuel(self)
