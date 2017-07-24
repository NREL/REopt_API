import math
import os
from collections import namedtuple
from datetime import datetime, timedelta

from reo.src.dat_file_manager import DatFileManager


class BuiltInProfile(object):

    library_path = os.path.join('Xpress', 'DatLibrary', 'LoadProfiles')
    Default_city = namedtuple("Default_city", "name lat lng")
    default_cities = [
        Default_city('Miami', 25.761680, -80.191790),
        Default_city('Houston', 29.760427, -95.369803),
        Default_city('Phoenix', 33.448377, -112.074037),
        Default_city('Atlanta', 33.748995, -84.387982),
        Default_city('LosAngeles', 34.052234, -118.243685),
        Default_city('SanFrancisco', 37.774929, -122.419416),
        Default_city('LasVegas', 36.114707, -115.172850),
        Default_city('Baltimore', 39.290385, -76.612189),
        Default_city('Albuquerque', 35.085334, -106.605553),
        Default_city('Seattle', 47.606209, -122.332071),
        Default_city('Chicago', 41.878114, -87.629798),
        Default_city('Boulder', 40.014986, -105.270546),
        Default_city('Minneapolis', 44.977753, -93.265011),
        Default_city('Helena', 46.588371, -112.024505),
        Default_city('Duluth', 46.786672, -92.100485),
        Default_city('Fairbanks', 64.837778, -147.716389),
    ]

    def __init__(self, latitude, longitude, load_size, load_monthly_kwh, load_profile_name, load_year, **kwargs):
        """

        :param latitude:
        :param longitude:
        :param annual_kwh:
        :param monthly_kwh: list of 12 floats for montly energy sums
        :param load_profile_name: building type chosen by user
        :param load_year: year of load profile, needed for monthly scaling
        :param kwargs:
        """

        self.city = self._nearest_city(latitude, longitude)
        self.annual_kwh = load_size if load_size else sum(load_monthly_kwh)
        self.monthly_kwh = load_monthly_kwh
        self.building_type = load_profile_name
        self.normalized_profile = self._normalized_profile()
        self.year = load_year

    def _normalized_profile(self):

        profile_path = os.path.join(BuiltInProfile.library_path, "Load8760_norm_" + self.city + "_" + self.building_type + ".dat")
        normalized_profile = list()
        f = open(profile_path, 'r')
        for line in f:
            normalized_profile.append(float(line.strip('\n')))

        return normalized_profile

    @property
    def built_in_profile(self):

        if self.annual_kwh:
            return [ld * self.annual_kwh for ld in self.normalized_profile]

        return self.monthly_scaled_profile

    @property
    def monthly_scaled_profile(self):

        load_profile = []

        datetime_current = datetime(self.year, 1, 1, 0)
        month_total = 0
        month_scale_factor = []

        for load in self.normalized_profile:
            month = datetime_current.month
            import pdb; pdb.set_trace()
            month_total += self.annual_kwh * load

            # add an hour
            datetime_current = datetime_current + timedelta(0, 0, 0, 0, 0, 1, 0)

            if month != datetime_current.month:
                if month_total == 0:
                    month_scale_factor.append(0)
                else:
                    month_scale_factor.append(float(self.monthly_kwh[month - 1] / month_total))
                month_total = 0

        datetime_current = datetime(self.year, 1, 1, 0)

        for load in self.normalized_profile:
            month = datetime_current.month

            load_profile.append(self.annual_kwh * load * month_scale_factor[month - 1])

            # add an hour
            datetime_current = datetime_current + timedelta(0, 0, 0, 0, 0, 1, 0)

        return load_profile

    def _nearest_city(self, lat, lng):
        min_distance = 1e9
        nearest_city = None

        for c in BuiltInProfile.default_cities:
            distance = math.sqrt((lat - c.lat)**2 + (lng - c.lng)**2)
            if distance < min_distance:
                min_distance = distance
                nearest_city = c.name
        return nearest_city


class LoadProfile(BuiltInProfile):

    def __init__(self, user_profile=None, crit_load_factor=None, outage_start=None, outage_end=None, **kwargs):

        self.annual_kwh = None
        self.load_list = None

        if user_profile:
            self.load_list = user_profile
            self.annual_kwh = sum(user_profile)

        else:  # building type and (load_size OR load_monthly_kwh) defined by user
            super(LoadProfile, self).__init__(**kwargs)
            self.load_list = self.built_in_profile
            self.annual_kwh = sum(self.load_list)

        if crit_load_factor and outage_start and outage_end:
            # modify load
            self.load_list = self.load_list[0:outage_start] \
                           + [ld * crit_load_factor for ld in self.load_list[outage_start:outage_end]] \
                           + self.load_list[outage_end:]
        dfm = DatFileManager()
        dfm.add_load(self)
