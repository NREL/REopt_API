#!/user/bin/python
# ==============================================================================
#  File: ~\Sunlamp\DatLibrarySetup\pvwatts\pvwatts.py
#
#  Date: July 15, 2016
#  Auth: N. DiOrio, N. Laws
#
#  Description: download pvwatts solar resource for given lat/lon
#       and produce 'ProdFactor' for Mosel (includes utility ProdFactor)
# ==============================================================================
import requests
import json
import os, csv


class PVWatts:
    # API specific
    key = "EkVFWynUReFEH8HT1L1RAe4C32RUx4w1AEtiN78J"
    base = "https://developer.nrel.gov/api/pvwatts/v5.json"

    # Input data
    latitude = []
    longitude = []
    run_id = []

    # Assume defaults
    dataset = "tmy3"  # Default: tmy2 Options: tmy2 , tmy3, intl
    inv_eff = 92  # or 96?
    dc_ac_ratio = 1.1
    azimuth = 180
    system_capacity = 1  # kw to get prod factor
    array_type = 0  # fixed open rack
    module_type = 0  # standard
    timeframe = "hourly"
    losses = 14
    radius = 0

    # Base url; lat, lon, and tilt=lat added in "download_locations"
    url_base = base + "?api_key=" + key + "&azimuth=" + str(azimuth) + "&system_capacity=" + str(system_capacity) + \
               "&losses=" + str(losses) + "&array_type=" + str(array_type) + "&module_type=" + str(module_type) + \
               "&timeframe=" + timeframe + "&dc_ac_ratio=" + str(dc_ac_ratio) + "&inv_eff=" + str(inv_eff) + \
               "&radius=" + str(radius) + "&dataset=" + dataset

    # Time
    steps_per_hour = 1

    # Output
    output_root = []
    prod_factor = []
    prod_factor_bau = []

    filename_GIS = []
    filename_GIS_bau = []

    def __init__(self, output_root, run_id, latitude, longitude, steps_per_hour=1):
        self.steps_per_hour = steps_per_hour
        self.output_root = output_root
        self.run_id = run_id

        self.latitude = latitude
        self.longitude = longitude

        self.download_locations()

    def download_locations(self):
        url = self.url_base + "&lat=" + str(self.latitude) + "&lon=" + str(self.longitude) + "&tilt=" + str(self.latitude)
        print url
        r = requests.get(url, verify=False)
        data = json.loads(r.text)
        self.compute_prod_factor(data)
        self.write_output()

    def compute_prod_factor(self, data):
        # NEED TO DERATE 0.5%! nlaws: accounted for in LevelizationFactor, which is defined in economics.py
        outputs = data['outputs']
        ac_hourly = outputs['ac']
        dc_nameplate = self.system_capacity * 1000  # W
        prod_factor = []
        prod_factor_bau = []
        prod_factor_ts = []

        # subhourly (i.e 15 minute data)
        if self.steps_per_hour >= 1:
            for hour in range(0, 8760):
                for step in range(0, self.steps_per_hour):
                    prod_factor_ts.append(round(ac_hourly[hour] / dc_nameplate, 4))
        # downscaled run (i.e 288 steps per year)
        else:
            for hour in range(0, 8760, int(1 / self.steps_per_hour)):
                prod_factor_ts.append(round(ac_hourly[hour] / dc_nameplate, 4))

        # build dictionary with same structure as ProdFactor in Mosel
        tech_bau = ['UTIL1']
        tech = ['PV', 'PVNM', 'UTIL1']
        load = ["1R", "1W", "1X", "1S"]
        pf_Dict = {}
        pf_Dict_bau = {}

        for t in tech:
            pf_Dict[t] = {ld: None for ld in load}
            if t is 'UTIL1':
                pf_Dict[t]['1R'] = pf_Dict[t]['1S'] = [1.0 for _ in range(
                    8760)]  # grid produces 100% of capacity, so '1's for Retail and Storage
                pf_Dict[t]['1W'] = pf_Dict[t]['1X'] = [0.0 for _ in range(
                    8760)]  # grid cannot sell back, so '0's for Wholesale and Xbin
            elif t is 'PV':
                pf_Dict[t]['1R'] = pf_Dict[t]['1S'] = \
                    pf_Dict[t]['1W'] = pf_Dict[t]['1X'] = [p for p in prod_factor_ts]  # PV can serve all loads
            elif t is 'PVNM':
                pf_Dict[t]['1R'] = pf_Dict[t]['1S'] = \
                    pf_Dict[t]['1W'] = pf_Dict[t]['1X'] = [p for p in prod_factor_ts]  # PV can serve all loads

        for t in tech_bau:
            pf_Dict_bau[t] = {ld: None for ld in load}
            if t is 'UTIL1':
                pf_Dict_bau[t]['1R'] = pf_Dict_bau[t]['1S'] = [1.0 for _ in range(8760)]
                pf_Dict_bau[t]['1W'] = pf_Dict_bau[t]['1X'] = [0.0 for _ in range(8760)]

        for t in tech:
            for ld in load:
                for pf in pf_Dict[t][ld]:
                    prod_factor.append(str(pf))
        for t in tech_bau:
            for ld in load:
                for pf in pf_Dict_bau[t][ld]:
                    prod_factor_bau.append(str(pf))

        self.prod_factor = prod_factor
        self.prod_factor_bau = prod_factor_bau

    def write_output(self):
        output_root = os.path.join(self.output_root, "GISdata")
        self.filename_GIS = "GIS_" + str(self.run_id) + ".dat"
        self.filename_GIS_bau = "GIS_" + str(self.run_id) + "_bau.dat"

        output = os.path.join(output_root, self.filename_GIS)
        output_bau = os.path.join(output_root, self.filename_GIS_bau)

        f = open(output, 'w')
        f_bau = open(output_bau, 'w')
        f.write("ProdFactor: [\n")
        f_bau.write("ProdFactor: [\n")
        for prod_factor in self.prod_factor:
            f.write(prod_factor + "\t,\n")
        for prod_factor in self.prod_factor_bau:
            f_bau.write(prod_factor + "\t,\n")
        f.write("]")
        f_bau.write("]")
        f.close()
        f_bau.close()
