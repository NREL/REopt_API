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
                 url_base="https://developer.nrel.gov/api/pvwatts/v5.json",
                 key=keys.pvwatts_api_key,
                 azimuth=180,
                 system_capacity=1,
                 losses=0.14,
                 array_type=0,
                 module_type=0,
                 timeframe='hourly',
                 gcr=0.4,
                 dc_ac_ratio=1.1,
                 inv_eff=0.96,
                 radius=0,
                 dataset="tmy3",
                 latitude=None,
                 longitude=None,
                 tilt=None,
                 time_steps_per_hour=1,
                 offline=False,
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

        if self.tilt is None:
            self.tilt = self.latitude

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
        resp = requests.get(self.url, verify=True)

        if not resp.ok:
            log("ERROR", "PVWatts status code {}. {}".format(resp.status_code, resp.content))
            raise Exception("PVWatts status code {}. {}".format(resp.status_code, resp.content))

        data = json.loads(resp.text)
        return data

    @property
    def pv_prod_factor(self):

        if not self.offline:

            outputs = self.data['outputs']
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
            prod_factor = list()
            import os
            with open(os.path.join('reo', 'tests', 'offline_pv_prod_factor.txt'), 'r') as f:
                for line in f:
                    prod_factor.append(float(line.strip('\n')))

        return prod_factor
