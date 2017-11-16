import math
import os
import copy
from collections import namedtuple
from datetime import datetime, timedelta
from reo.api_definitions import default_cities, default_tmyid
import requests


class BuiltInProfile(object):

    library_path = os.path.join('Xpress', 'DatLibrary', 'LoadProfiles')
    
    Default_city = namedtuple("Default_city", "name lat lng tmyid")
    
    default_cities = [
        Default_city('Miami', 25.761680, -80.191790, 722020),
        Default_city('Houston', 29.760427, -95.369803, 722430),
        Default_city('Phoenix', 33.448377, -112.074037, 722780),
        Default_city('Atlanta', 33.748995, -84.387982, 722190),
        Default_city('LosAngeles', 34.052234, -118.243685, 722950),
        Default_city('SanFrancisco', 37.774929, -122.419416, 724940),
        Default_city('Baltimore', 39.290385, -76.612189, 724060),
        Default_city('Albuquerque', 35.085334, -106.605553, 723650),
        Default_city('Seattle', 47.606209, -122.332071, 727930),
        Default_city('Chicago', 41.878114, -87.629798, 725300),
        Default_city('Boulder', 40.014986, -105.270546, 724699),
        Default_city('Minneapolis', 44.977753, -93.265011, 726580),
        Default_city('Helena', 46.588371, -112.024505, 727720),
        Default_city('Duluth', 46.786672, -92.100485, 727450),
        Default_city('Fairbanks', 64.837778, -147.716389, 702610),
    ]

    annual_loads = {
        'Albuquerque': {
            'fastfoodrest': 193235,
            'fullservicerest': 367661,
            'hospital': 8468546,
            'largehotel': 2407649,
            'largeoffice': 6303595,
            'mediumoffice': 884408,
            'midriseapartment': 269734,
            'outpatient': 1678720,
            'primaryschool': 1070908,
            'retailstore': 505417,
            'secondaryschool': 2588879,
            'smallhotel': 755373,
            'smalloffice': 87008,
            'stripmall': 497132,
            'supermarket': 1947654,
            'warehouse': 228939,
            'flatload': 500000
        },
        'Atlanta': {
            'fastfoodrest': 197467,
            'fullservicerest': 353750,
            'hospital': 9054747,
            'largehotel': 2649819,
            'largeoffice': 6995864,
            'mediumoffice': 929349,
            'midriseapartment': 285349,
            'outpatient': 1672434,
            'primaryschool': 1128702,
            'retailstore': 543340,
            'secondaryschool': 2849901,
            'smallhotel': 795777,
            'smalloffice': 90162,
            'stripmall': 529719,
            'supermarket': 2092966,
            'warehouse': 223009,
            'flatload': 500000
        },
        'Baltimore': {
            'fastfoodrest': 192831,
            'fullservicerest': 341893,
            'hospital': 8895223,
            'largehotel': 2534272,
            'largeoffice': 6836130,
            'mediumoffice': 945425,
            'midriseapartment': 273225,
            'outpatient': 1623103,
            'primaryschool': 1077312,
            'retailstore': 510257,
            'secondaryschool': 2698987,
            'smallhotel': 767538,
            'smalloffice': 86112,
            'stripmall': 504715,
            'supermarket': 2018760,
            'warehouse': 229712,
            'flatload': 500000
        },
        'Boulder': {
            'fastfoodrest': 189092,
            'fullservicerest': 334005,
            'hospital': 8281865,
            'largehotel': 2313151,
            'largeoffice': 6127030,
            'mediumoffice': 884726,
            'midriseapartment': 255428,
            'outpatient': 1621950,
            'primaryschool': 1018424,
            'retailstore': 504256,
            'secondaryschool': 2441588,
            'smallhotel': 736174,
            'smalloffice': 84900,
            'stripmall': 495018,
            'supermarket': 1956244,
            'warehouse': 243615,
            'flatload': 500000
        },
        'Chicago': {
            'fastfoodrest': 189558,
            'fullservicerest': 333659,
            'hospital': 8567087,
            'largehotel': 2402021,
            'largeoffice': 6369028,
            'mediumoffice': 972772,
            'midriseapartment': 265528,
            'outpatient': 1587062,
            'primaryschool': 1045477,
            'retailstore': 513106,
            'secondaryschool': 2568086,
            'smallhotel': 759657,
            'smalloffice': 86224,
            'stripmall': 506886,
            'supermarket': 2025507,
            'warehouse': 245750,
            'flatload': 500000
        },
        'Duluth': {
            'fastfoodrest': 183713,
            'fullservicerest': 318867,
            'hospital': 8134328,
            'largehotel': 2231678,
            'largeoffice': 6036003,
            'mediumoffice': 1032533,
            'midriseapartment': 256393,
            'outpatient': 1534322,
            'primaryschool': 982163,
            'retailstore': 532503,
            'secondaryschool': 2333466,
            'smallhotel': 752284,
            'smalloffice': 83759,
            'stripmall': 500979,
            'supermarket': 1980986,
            'warehouse': 256575,
            'flatload': 500000
        },
        'Fairbanks': {
            'fastfoodrest': 182495,
            'fullservicerest': 314760,
            'hospital': 7899166,
            'largehotel': 2181664,
            'largeoffice': 5956232,
            'mediumoffice': 1267132,
            'midriseapartment': 271840,
            'outpatient': 1620270,
            'primaryschool': 986128,
            'retailstore': 573411,
            'secondaryschool': 2344790,
            'smallhotel': 831480,
            'smalloffice': 86614,
            'stripmall': 545421,
            'supermarket': 2033295,
            'warehouse': 285064,
            'flatload': 500000
        },
        'Helena': {
            'fastfoodrest': 185877,
            'fullservicerest': 325263,
            'hospital': 8068698,
            'largehotel': 2246239,
            'largeoffice': 6003137,
            'mediumoffice': 930630,
            'midriseapartment': 252659,
            'outpatient': 1568262,
            'primaryschool': 994496,
            'retailstore': 534933,
            'secondaryschool': 2357548,
            'smallhotel': 729797,
            'smalloffice': 84219,
            'stripmall': 503504,
            'supermarket': 1969137,
            'warehouse': 252245,
            'flatload': 500000
        },
        'Houston': {
            'fastfoodrest': 210283,
            'fullservicerest': 383987,
            'hospital': 9634661,
            'largehotel': 3050370,
            'largeoffice': 7539308,
            'mediumoffice': 972535,
            'midriseapartment': 335063,
            'outpatient': 1756541,
            'primaryschool': 1258146,
            'retailstore': 589419,
            'secondaryschool': 3421024,
            'smallhotel': 863952,
            'smalloffice': 98508,
            'stripmall': 577987,
            'supermarket': 2225265,
            'warehouse': 221593,
            'flatload': 500000
        },
        'LosAngeles': {
            'fastfoodrest': 188857,
            'fullservicerest': 352240,
            'hospital': 8498389,
            'largehotel': 2458786,
            'largeoffice': 6642784,
            'mediumoffice': 846742,
            'midriseapartment': 248028,
            'outpatient': 1565008,
            'primaryschool': 1095263,
            'retailstore': 486188,
            'secondaryschool': 2584380,
            'smallhotel': 751880,
            'smalloffice': 86655,
            'stripmall': 491972,
            'supermarket': 1935886,
            'warehouse': 182085,
            'flatload': 500000
        },
        'Miami': {
            'fastfoodrest': 224494,
            'fullservicerest': 448713,
            'hospital': 10062043,
            'largehotel': 3437188,
            'largeoffice': 8002063,
            'mediumoffice': 1021224,
            'midriseapartment': 424956,
            'outpatient': 1929148,
            'primaryschool': 1426635,
            'retailstore': 635086,
            'secondaryschool': 4074081,
            'smallhotel': 972090,
            'smalloffice': 108279,
            'stripmall': 675793,
            'supermarket': 2260929,
            'warehouse': 202082,
            'flatload': 500000
        },
        'Minneapolis': {
            'fastfoodrest': 188368,
            'fullservicerest': 330920,
            'hospital': 8425063,
            'largehotel': 2378872,
            'largeoffice': 6306693,
            'mediumoffice': 1005875,
            'midriseapartment': 267383,
            'outpatient': 1582701,
            'primaryschool': 1022667,
            'retailstore': 539203,
            'secondaryschool': 2498647,
            'smallhotel': 774571,
            'smalloffice': 85921,
            'stripmall': 511567,
            'supermarket': 2034650,
            'warehouse': 249332,
            'flatload': 500000
        },
        'Phoenix': {
            'fastfoodrest': 216088,
            'fullservicerest': 389739,
            'hospital': 9265786,
            'largehotel': 2990053,
            'largeoffice': 7211666,
            'mediumoffice': 1004988,
            'midriseapartment': 378378,
            'outpatient': 1849358,
            'primaryschool': 1289084,
            'retailstore': 593924,
            'secondaryschool': 3503727,
            'smallhotel': 881843,
            'smalloffice': 104583,
            'stripmall': 590954,
            'supermarket': 2056195,
            'warehouse': 241585,
            'flatload': 500000
        },
        'SanFrancisco': {
            'fastfoodrest': 183953,
            'fullservicerest': 317124,
            'hospital': 7752817,
            'largehotel': 2206880,
            'largeoffice': 6085403,
            'mediumoffice': 792199,
            'midriseapartment': 229671,
            'outpatient': 1394447,
            'primaryschool': 1009369,
            'retailstore': 449025,
            'secondaryschool': 2327074,
            'smallhotel': 698095,
            'smalloffice': 78132,
            'stripmall': 455802,
            'supermarket': 1841655,
            'warehouse': 185889,
            'flatload': 500000
        },
        'Seattle': {
            'fastfoodrest': 184142,
            'fullservicerest': 318741,
            'hospital': 7912504,
            'largehotel': 2212410,
            'largeoffice': 6019271,
            'mediumoffice': 878390,
            'midriseapartment': 237242,
            'outpatient': 1434195,
            'primaryschool': 983498,
            'retailstore': 455854,
            'secondaryschool': 2282972,
            'smallhotel': 693921,
            'smalloffice': 79716,
            'stripmall': 460449,
            'supermarket': 1868973,
            'warehouse': 210300,
            'flatload': 500000
        },
    }

    default_buildings = ['fastfoodrest',
                         'fullservicerest',
                         'hospital',
                         'largehotel',
                         'largeoffice',
                         'mediumoffice',
                         'midriseapartment',
                         'outpatient',
                         'primaryschool',
                         'retailstore',
                         'secondaryschool',
                         'smallhotel',
                         'smalloffice',
                         'stripmall',
                         'supermarket',
                         'warehouse',
                         'flatload',
                         ]

    def __init__(self, latitude=None, longitude=None, doe_reference_name='', annual_kwh=None, year=None,
                 monthly_totals_kwh=None, **kwargs):
        """
        :param latitude: float
        :param longitude: float
        :param annual_kwh: float or int
        :param monthly_kwh: list of 12 floats for monthly energy sums
        :param doe_reference_name: building type chosen by user
        :param year: year of load profile, needed for monthly scaling
        :param kwargs:
        """

        self.latitude = float(latitude) if latitude else None
        self.longitude = float(longitude) if longitude else None
        self.monthly_kwh = monthly_totals_kwh
        self.doe_reference_name = doe_reference_name
        self.annual_kwh = annual_kwh if annual_kwh else (sum(monthly_totals_kwh) if monthly_totals_kwh else self.default_annual_kwh)
        self.year = year

    @property
    def built_in_profile(self):
        if self.monthly_kwh is None:
            return [ld * self.annual_kwh for ld in self.normalized_profile]

        return self.monthly_scaled_profile

    @property
    def city(self):
        if self.latitude is not None and self.longitude is not None:
            if hasattr(self, 'nearest_city'):
                return self.nearest_city
            else:
                search_radius = str(25)
                ashrae_tmy = default_tmyid()[0]
                ashrae_url = "http://developer.nrel.gov/api/reo/v3.json?api_key=653bcca1955c8acf748bcf5ce9a953f7b2e23629&lat=" \
                             + str(self.latitude) + "&lon=" + str(self.longitude) + "&distance=" + search_radius + "&output_fields=ashrae_tmy"
                r = requests.get(ashrae_url)

                if r.status_code == 200 and "ashrae_tmy" in r.json()["outputs"] and "tmy_id" in r.json()["outputs"]["ashrae_tmy"]:
                    ashrae_tmy_id = r.json()["outputs"]["ashrae_tmy"]["tmy_id"]

                    if ashrae_tmy_id in default_tmyid():
                        self.nearest_city = default_cities()[default_tmyid().index(ashrae_tmy_id)]
                    else:
                        raise AttributeError('load_profile', 'Unexpected climate zone returned by remote database')

                    return self.nearest_city
                else:
                    raise AttributeError('load_profile', 'Failed to return climate zone from database')

        else:
            raise AttributeError('load_profile', 'Cannot determine nearest city - missing city or latitude and longitude inputs')

    @property
    def default_annual_kwh(self):
        if self.city and self.building_type:
            return self.annual_loads[self.city][self.building_type.lower()]
        return None

    @property
    def building_type(self):
        name = self.doe_reference_name.replace(' ','')
        if name.lower() not in self.default_buildings:
            raise AttributeError('load_profile', "Invalid doe_reference_name. Select from the following:\n{}".format(self.default_buildings))
        return name

    @property
    def monthly_scaled_profile(self):

        load_profile = []

        datetime_current = datetime(self.year, 1, 1, 0)
        month_total = 0
        month_scale_factor = []

        for load in self.normalized_profile:
            month = datetime_current.month
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

    @property
    def normalized_profile(self):

        profile_path = os.path.join(BuiltInProfile.library_path, "Load8760_norm_" + self.city + "_" + self.building_type + ".dat")
        normalized_profile = list()
        f = open(profile_path, 'r')
        for line in f:
            normalized_profile.append(float(line.strip('\n')))

        return normalized_profile


class LoadProfile(BuiltInProfile):

    def __init__(self, dfm, user_profile=None, critical_load_pct=None, outage_start_hour=None, outage_end_hour=None, **kwargs):

        if user_profile:
            self.load_list = user_profile

        else:  # building type and (annual_kwh OR monthly_totals_kwh) defined by user
            super(LoadProfile, self).__init__(**kwargs)
            self.load_list = self.built_in_profile

        self.unmodified_load_list = copy.copy(self.load_list)
        self.bau_load_list = copy.copy(self.load_list)

        if None not in [critical_load_pct, outage_start_hour, outage_end_hour]:
            # modify load
            self.load_list = self.load_list[0:outage_start_hour] \
                           + [ld * critical_load_pct for ld in self.load_list[outage_start_hour:outage_end_hour]] \
                           + self.load_list[outage_end_hour:]
            self.bau_load_list = self.load_list[0:outage_start_hour] \
                                + [0 for _ in self.load_list[outage_start_hour:outage_end_hour]] \
                                + self.load_list[outage_end_hour:]

        self.annual_kwh = sum(self.load_list)
        self.bau_annual_kwh = sum(self.bau_load_list)
        dfm.add_load(self)
