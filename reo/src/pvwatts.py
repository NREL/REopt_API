#!/user/bin/python
# ==============================================================================
#  Description: download pvwatts solar resource for given lat/lon
#       and produce 'ProdFactor' for Mosel
# ==============================================================================
import requests
import json
import keys
from reo.log_levels import log


class PVWatts:

    def __init__(self,
                 url_base="https://developer.nrel.gov/api/pvwatts/v6.json",
                 key=keys.developer_nrel_gov_key,
                 azimuth=180,
                 system_capacity=1,
                 losses=0.14,
                 array_type=0,
                 module_type=0,
                 timeframe='hourly',
                 gcr=0.4,
                 dc_ac_ratio=1.1,
                 inv_eff=0.96,
                 radius=100,
                 dataset="nsrdb",
                 latitude=None,
                 longitude=None,
                 tilt=None,
                 time_steps_per_hour=1,
                 offline=False,
                 verify=True,
                 **kwargs):

        self.url_base = url_base
        self.key = key
        self.azimuth = azimuth
        self.system_capacity = system_capacity
        self.losses = losses
        self.array_type = array_type
        self.module_type = module_type
        self.timeframe = timeframe
        self.gcr = gcr
        self.dc_ac_ratio = dc_ac_ratio
        self.inv_eff = inv_eff
        self.radius = radius
        self.dataset = dataset
        self.latitude = latitude
        self.longitude = longitude
        self.tilt = tilt
        self.time_steps_per_hour = time_steps_per_hour
        self.offline = offline  # used for testing
        self.verify = verify  # used for testing
        self.response = None
        self.response = self.data  # store response so don't hit API multiple times

        if self.tilt is None:
            if self.latitude < 0: # if the site is in the southern hemisphere, and no tilt has been specified, then set the tilt to the positive latitude value and change the azimuth to zero
                self.tilt = self.latitude * -1
                self.azimuth = 0
            else:
                self.tilt = self.latitude # if the site is in the norther hemisphere, and no tilt has been specified, then set the tilt to the latitude value and leave the azimuth at 180

    @property
    def url(self):
        url = self.url_base + "?api_key=" + self.key + "&azimuth=" + str(self.azimuth) + \
              "&system_capacity=" + str(self.system_capacity) + "&losses=" + str(self.losses*100) + \
              "&array_type=" + str(self.array_type) + "&module_type=" + str(self.module_type) + \
              "&timeframe=" + self.timeframe +"&gcr=" + str(self.gcr) +  "&dc_ac_ratio=" + str(self.dc_ac_ratio) + \
              "&inv_eff=" + str(self.inv_eff*100) + "&radius=" + str(int(self.radius)) + "&dataset=" + self.dataset + \
              "&lat=" + str(self.latitude) + "&lon=" + str(self.longitude) + "&tilt=" + str(self.tilt)
        return url

    @property
    def data(self):

        if self.response is None:
            resp = requests.get(self.url, verify=self.verify)
            if not resp.ok:
                # check for international location
                data = json.loads(resp.text)
                intl_warning = "This location appears to be outside the US"
                
                if (intl_warning in s for s in data.get("warnings",[])):
                    self.dataset = "intl"
                    self.radius = self.radius * 2 # bump up search radius, since there aren't many sites
                    resp = requests.get(self.url, verify=self.verify)

            if not resp.ok:
                log.error("PVWatts status code {}. {}".format(resp.status_code, resp.content))
                raise Exception("PVWatts status code {}. {}".format(resp.status_code, resp.content))

            log.info("PVWatts API query successful.")
            data = json.loads(resp.text)
            self.response = data

        return self.response

    @property
    def pv_prod_factor(self):

        if not self.offline:

            outputs = self.response['outputs']
            ac_hourly = outputs.get('ac')

            if ac_hourly is None:
                ac_hourly = [0] * 8760

            dc_nameplate = self.system_capacity * 1000  # W
            prod_factor = []

            # subhourly (i.e 15 minute data)
            if self.time_steps_per_hour >= 1:
                timesteps = []
                timesteps_base = range(0, 8760)
                for ts_b in timesteps_base:
                    for step in range(0, self.time_steps_per_hour):
                       timesteps.append(ts_b)

            # downscaled run (i.e 288 steps per year)
            else:
                timesteps = range(0, 8760, int(1 / self.time_steps_per_hour))

            for hour in timesteps:
                # degradation (levelization factor) applied in mosel model
                prod_factor.append(round(ac_hourly[hour]/ dc_nameplate, 4))

        else:
            prod_factor_original = list()
            prod_factor = list()
            import os
            with open(os.path.join('reo', 'tests', 'offline_pv_prod_factor.txt'), 'r') as f:
                for line in f:
                    prod_factor_original.append(float(line.strip('\n')))

            # the stored values in offline_pv_prod_factor.txt are 8760 rows, thus modifying prod_factor list
            # to have 8760*4 values

            prod_factor = [val for val in prod_factor_original for _ in range(self.time_steps_per_hour)]

        return prod_factor
