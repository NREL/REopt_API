from reo.src.load_profile import BuiltInProfile
import json
import os
import copy
import numpy as np


class LoadProfileBoilerFuel(BuiltInProfile):
    """
    Boiler Load Profiles based on CRB defined load shapes or user-defined input
    """
    with open(os.path.join(BuiltInProfile.library_path, 'reference_heating_mmbtu.json'), 'r') as f:
        annual_loads = json.loads(f.read())

    builtin_profile_prefix = "Heating8760_norm_"
    
    def __init__(self, dfm=None, latitude = None, longitude = None, nearest_city = None, time_steps_per_hour = None, 
                    year = None, **kwargs):
        """
        :param dfm: (object) data_manager to which this load object will be added
        :param latitude: (float) site latitude
        :param longitude: (float) site longitude
        :param nearest_city: (str) site nearest_city
        :param time_steps_per_hour: (int) simulation time resolution
        :param year: (int) electric LoadProfile year
        :param kwargs: (dict) Chiller specific inputs as defined in reo/nested_inputs
        """
        
        if kwargs.get('loads_mmbtu_per_hour') is not None: 
            self.load_list = kwargs['loads_mmbtu_per_hour']
            self.annual_mmbtu = sum(self.load_list)

        else:  # building type and (annual_mmbtu OR monthly_mmbtu) defined by user
            doe_reference_name = kwargs['doe_reference_name']
            combine_loadlist = []
            for i in range(len(doe_reference_name)):
                # Monthly loads can only be used to scale a non-hybrid profile
                kwargs['monthly_totals_energy'] = kwargs.get("monthly_mmbtu")
                if len(doe_reference_name)>1:
                    kwargs['monthly_totals_energy'] = None
                # We only scale by percent share if a raw annual tonhour value has not been provided
                
                kwargs['annual_energy'] = None
                # We only scale by percent share if a raw annual tonhour value has not been provided
                if (kwargs.get("annual_mmbtu") or None) is not None:
                    kwargs['annual_energy'] = kwargs["annual_mmbtu"]
                    percent_share = 100
                else:
                    percent_share = kwargs.get("percent_share")[i]
                kwargs['annual_loads'] = self.annual_loads
                kwargs['builtin_profile_prefix'] = self.builtin_profile_prefix
                kwargs['latitude'] = latitude
                kwargs['longitude'] = longitude
                kwargs['doe_reference_name'] = doe_reference_name[i]
                kwargs['nearest_city'] = nearest_city
                kwargs['time_steps_per_hour'] = time_steps_per_hour
                kwargs['year'] = year
                super(LoadProfileBoilerFuel, self).__init__(**kwargs)
                if time_steps_per_hour > 1:
                    partial_load_list = np.concatenate([[x] * time_steps_per_hour \
                                                            for x in self.built_in_profile])
                else:
                    partial_load_list = self.built_in_profile
            
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
            self.load_list = copy.copy(hybrid_loadlist)
            self.annual_mmbtu = sum(self.load_list)

        if dfm is not None:
            dfm.add_load_boiler_fuel(self)
