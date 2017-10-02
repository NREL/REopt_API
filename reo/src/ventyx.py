import os
# import pandas as pd


class Ventyx(object):

    @property
    def wind_prod_factor(self):

        # csv_file = os.path.join('static', 'files', '50009-2011.csv')
        # d = pd.DataFrame.from_csv(csv_file)
        # wind_speeds = d.loc[:, 'wind speed at 100m (m/s)'].tolist()

        src_file = os.path.join('reo', 'tests', 'NWTC_pfs.txt')
        with open(src_file, 'r') as f:
            wind_speeds = f.read().split('\r')
        wind_speeds = [float(s) for s in wind_speeds]
        interval = len(wind_speeds)/8760

        hourly = []
        for idx in range(0, len(wind_speeds), interval):
            hourly.append(sum(wind_speeds[idx:idx+interval]) / float(interval))

        return hourly
