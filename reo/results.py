import os
import pandas as pd
from api_definitions import *
import pro_forma as pf


class Results:

    # data
    df_results = []
    df_results_base = []
    df_cols = ['Variable', 'Value']
    economics = []

    # paths
    path_output = []
    path_output_base = []
    path_summary = []
    path_summary_base = []
    path_proforma = []

    # file names
    file_summary = 'summary.csv'
    file_proforma = 'ProForma.xlsx'

    # outputs that need to get added to DB
    lcc_bau = None
    year_one_energy_cost = None
    year_one_energy_cost_bau = None
    year_one_energy_savings = None
    year_one_demand_cost = None
    year_one_demand_cost_bau = None
    year_one_demand_savings = None
    year_one_energy_exported = None
    lcc = None
    irr = None
    npv = None
    pv_kw = None
    batt_kw = None
    batt_kwh = None


    def outputs(self, **args):
        return outputs(**args)

    def __init__(self, path_output, path_output_base, economics):

        self.path_output = path_output
        self.path_output_base = path_output_base
        self.path_summary = os.path.join(path_output, self.file_summary)
        self.path_summary_base = os.path.join(path_output_base, self.file_summary)
        self.path_proforma = os.path.join(path_output, self.file_proforma)
        self.economics = economics

        for k in self.outputs():
            setattr(self, k, None)

    def run(self):

        self.load_results()
        self.compute_value()
        self.generate_pro_forma()

    def load_results(self):

        df_results = pd.read_csv(self.path_summary, header=None, names=self.df_cols, index_col=0)
        df_results_base = pd.read_csv(self.path_summary_base, header=None, names=self.df_cols, index_col=0)

        df_results = df_results.transpose()
        df_results_base = df_results_base.transpose()

        if self.is_optimal(df_results) and self.is_optimal(df_results_base):
            self.populate_data(df_results)
            self.populate_data_bau(df_results_base)

        self.update_types()

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
            pv_kw += float(df['PVNM Size (kW)'].values[0])
        if 'PV Size (kW)' in df.columns:
            pv_kw += float(df['PV Size (kW)'].values[0])
        if 'Utility_kWh' in df.columns:
            self.utility_kwh = float(df['Utility_kWh'].values[0])
        if 'Year 1 Energy Cost ($)' in df.columns:
            self.year_one_energy_cost = float(df['Year 1 Energy Cost ($)'].values[0])
        if 'Year 1 Demand Cost ($)' in df.columns:
            self.year_one_demand_cost = float(df['Year 1 Demand Cost ($)'].values[0])
        if 'Total Electricity Exported (kWh)' in df.columns:
            self.year_one_energy_exported = float(df['Total Electricity Exported (kWh)'].values[0])

        self.pv_kw = pv_kw

    def populate_data_bau(self, df):

        if 'LCC ($)' in df.columns:
            self.lcc_bau = float(df['LCC ($)'].values[0])
        if 'Year 1 Energy Cost ($)' in df.columns:
            self.year_one_energy_cost_bau = float(df['Year 1 Energy Cost ($)'].values[0])
        if 'Year 1 Demand Cost ($)' in df.columns:
            self.year_one_demand_cost_bau = float(df['Year 1 Demand Cost ($)'].values[0])

    def compute_value(self):

        self.npv = self.lcc_bau - self.lcc
        self.year_one_demand_savings = self.year_one_demand_cost_bau - self.year_one_demand_cost
        self.year_one_energy_savings = self.year_one_energy_cost_bau - self.year_one_energy_cost

    def generate_pro_forma(self):

        # doesn't handle:
        # - if batt replacement kw cost is different from replacement kwh cost
        # - if PV or Batt do not have the same itc_rate

        econ = self.economics

        d = pf.ProForma(getattr(econ, 'analysis_period'),
                        getattr(econ, 'offtaker_discount_rate_nominal'),
                        getattr(econ, 'offtaker_tax_rate'),
                        getattr(econ, 'bonus_fraction'),
                        getattr(econ, 'rate_itc'), # modify based on updated incentives
                        getattr(econ, 'rate_escalation_nominal'),
                        getattr(econ, 'rate_inflation'),
                        getattr(econ, 'pv_om'),
                        getattr(econ, 'pv_cost'),
                        self.pv_kw,
                        getattr(econ, 'batt_cost_kwh'),
                        self.batt_kwh,
                        getattr(econ, 'batt_cost_kw'),
                        self.batt_kw,
                        getattr(econ, 'batt_replacement_cost_kwh'), # modify based on updated input
                        getattr(econ, 'batt_replacement_cost_kwh'),
                        self.year_one_energy_savings,
                        self.year_one_demand_savings,
                        self.year_one_energy_exported,
                        getattr(econ, 'rate_degradation'),
                        self.lcc,
                        self.lcc_bau)

        d.make_pro_forma(self.path_proforma)
        self.irr = d.get_IRR()

    def update_types(self):

        for group in [self.outputs()]:
            for k, v in group.items():
                value = getattr(self, k)

                if value is not None:
                    if v['type'] == float:
                        if v['pct']:
                            if value > 1.0:
                                setattr(self, k, float(value) * 0.01)

                    elif v['type'] == list:
                        value = [float(i) for i in getattr(self, k)]
                        setattr(self, k, value)

                    else:
                        setattr(self, k, v['type'](value))