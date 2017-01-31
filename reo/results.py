import os
#import pro_forma
import pandas as pd
from api_definitions import *


class Results:

    # data frames
    df_results = []
    df_results_base = []
    df_cols = ['Variable', 'Value']

    # paths
    path_output = []
    path_output_base = []
    path_summary = []
    path_summary_base = []

    # file names
    file_summary = 'summary.csv'

    def outputs(self, **args):
        return outputs(**args)

    def __init__(self, path_output, path_output_base):

        self.path_output = path_output
        self.path_output_base = path_output_base
        self.path_summary = os.path.join(path_output, self.file_summary)
        self.path_summary_base = os.path.join(path_output_base, self.file_summary)

        for k in self.outputs():
            setattr(self, k, None)

    def load_results(self):

        df_results = pd.read_csv(self.path_summary, header=None, names=self.df_cols, index_col=0)
        df_results_base = pd.read_csv(self.path_summary_base, header=None, names=self.df_cols, index_col=0)

        df_results = df_results.transpose()
        df_results_base = df_results_base.transpose()

        if self.is_optimal(df_results) and self.is_optimal(df_results_base):
            self.populate_data(df_results)

    def is_optimal(self, df):

        if 'Problem status' in df.columns:
            self.status = str(df['Problem status'].values[0]).rstrip()
            return self.status == "Optimum found"

    def populate_data(self, df):

        pv_kw = 0
        if 'LCC ($)' in df.columns:
            self.lcc = float(df['LCC ($)'].values[0])
        if 'Battery Power (kW)' in df.columns:
            self.batt_kw = float(df['Battery Power (kW)'].values[0])
        if 'Battery Capacity (kWh)' in df.columns:
            self.batt_kwh = float(df['Battery Capacity (kWh)'].values[0])
        if 'PVNM Size (kW)' in df.columns:
            pv_kw += round(float(df['PVNM Size (kW)'].values[0]), 0)
        if 'PV Size (kW)' in df.columns:
            pv_kw += round(float(df['PV Size (kW)'].values[0]), 0)
        if 'Utility_kWh' in df.columns:
            self.utility_kwh = float(df['Utility_kWh'].values[0])

        self.pv_kw = pv_kw
        self.update_types()

    def compute_npv(self):
        self.npv = float(self.df_results_base['LCC ($)'].values[0]) - float(self.df_results['LCC ($)'].values[0])

    def update_types(self):

        for group in [self.outputs()]:
            for k,v in group.items():
                value = getattr(self,k)

                if value is not None:
                    if v['type']==float:
                        if v['pct']:
                            if value > 1.0:
                                setattr(self, k, float(value)*0.01)

                    elif v['type'] == list:
                        value = [float(i) for i in getattr(self, k)]
                        setattr(self, k, value)

                    else:
                        setattr(self,k,v['type'](value))