import os
import pandas as pd


class Ventyx(object):

    def wind_prod_factor(self):

        csv_file = os.path.join('..', '..', 'static', 'files', '50009-2011.csv')
        d = pd.DataFrame.from_csv(csv_file)
        wind_speeds = d.loc[:, 'wind speed at 100m (m/s)'].tolist()
        interval = len(wind_speeds)/8760

        hourly = []
        for idx in range(0, len(wind_speeds), interval):
            hourly.append(sum(wind_speeds[idx:idx+interval]) / float(interval))
        print len(hourly)
