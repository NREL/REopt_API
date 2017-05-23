import os
import pandas as pd
from api_definitions import *
import pro_forma_writer as pf
import dispatch
from datetime import datetime
from tastypie.exceptions import ImmediateHttpResponse


class Results:

    # data
    df_cols = ['Variable', 'Value']

    # file names
    file_summary = 'summary.csv'
    file_proforma = 'ProForma.xlsx'
    file_dispatch = 'Dispatch.csv'

    # time outputs (scalar)
    time_steps_per_hour = 1

    # time series labels
    label_year_one_electric_load_series = 'Electric load'
    label_year_one_pv_to_battery_series = 'PV to battery'
    label_year_one_pv_to_load_series = 'PV to load'
    label_year_one_pv_to_grid_series = 'PV to grid'
    label_year_one_grid_to_load_series = 'Grid to load'
    label_year_one_grid_to_battery_series = 'Grid to battery'
    label_year_one_battery_to_load_series = 'Battery to load'
    label_year_one_battery_to_grid_series = 'Battery to grid'
    label_year_one_battery_soc_series = 'State of charge'
    label_year_one_energy_cost_series = 'Energy Cost ($/kWh)'
    label_year_one_demand_cost_series = 'Demand Cost ($/kW)'

    # time series outputs

    def outputs(self, **args):
        return outputs(**args)

    def __init__(self, path_templates, path_output, path_output_base, economics, year):

        self.path_templates = path_templates
        self.path_output = path_output
        self.path_output_base = path_output_base
        self.path_summary = os.path.join(path_output, self.file_summary)
        self.path_summary_base = os.path.join(path_output_base, self.file_summary)
        self.path_proforma = os.path.join(path_output, self.file_proforma)
        self.economics = economics
        self.year = year

        for k in self.outputs():
            setattr(self, k, None)

        # data
        self.df_results = []
        self.df_results_base = []

        # scalar outputs
        self.status = None
        self.lcc_bau = None
        self.year_one_utility_kwh = None
        self.year_one_energy_cost = None
        self.year_one_energy_cost_bau = None
        self.year_one_energy_savings = None
        self.year_one_demand_cost = None
        self.year_one_demand_cost_bau = None
        self.year_one_demand_savings = None
        self.year_one_payments_to_third_party_owner = None
        self.year_one_energy_exported = None
        self.total_energy_cost = None
        self.total_energy_cost_bau = None
        self.total_demand_cost = None
        self.total_demand_cost_bau = None
        self.total_payments_to_third_party_owner = None
        self.net_capital_costs_plus_om = None
        self.average_yearly_pv_energy_produced = None
        self.lcc = None
        self.irr = None
        self.npv = None
        self.pv_kw = None
        self.batt_kw = None
        self.batt_kwh = None
        self.year_one_datetime_start = None

        # time series outputs
        self.zero_array = 8760 * self.time_steps_per_hour * [0]
        self.year_one_electric_load_series = self.zero_array
        self.year_one_pv_to_battery_series = self.zero_array
        self.year_one_pv_to_load_series = self.zero_array
        self.year_one_pv_to_grid_series = self.zero_array
        self.year_one_grid_to_load_series = self.zero_array
        self.year_one_grid_to_battery_series = self.zero_array
        self.year_one_battery_to_load_series = self.zero_array
        self.year_one_battery_to_grid_series = self.zero_array
        self.year_one_battery_soc_series = self.zero_array
        self.year_one_energy_cost_series = self.zero_array
        self.year_one_demand_cost_series = self.zero_array

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
            self.compute_dispatch(df_results)
        else:
            raise ImmediateHttpResponse("No solution could be found for these inputs")

        self.update_types()

    def is_optimal(self, df):

        if 'Problem status' in df.columns:
            self.status = str(df['Problem status'].values[0]).rstrip()
            return self.status == "Optimum found"

    def populate_data(self, df):

        if 'LCC ($)' in df.columns:
            self.lcc = float(df['LCC ($)'].values[0])
        if 'Battery Power (kW)' in df.columns:
            self.batt_kw = float(df['Battery Power (kW)'].values[0])
        if 'Battery Capacity (kWh)' in df.columns:
            self.batt_kwh = float(df['Battery Capacity (kWh)'].values[0])

        # PV and PVNM are mutually exclusive, can't have both
        if 'PVNM Size (kW)' in df.columns:
            if float(df['PVNM Size (kW)'].values[0]) > 0:
                self.pv_kw = float(df['PVNM Size (kW)'].values[0])
        if 'PV Size (kW)' in df.columns:
            if float(df['PV Size (kW)'].values[0]) > 0:
                self.pv_kw = float(df['PV Size (kW)'].values[0])

        if 'Year 1 Energy Supplied From Grid (kWh)' in df.columns:
            self.year_one_utility_kwh = float(df['Year 1 Energy Supplied From Grid (kWh)'].values[0])
        if 'Year 1 Energy Cost ($)' in df.columns:
            self.year_one_energy_cost = float(df['Year 1 Energy Cost ($)'].values[0])
        if 'Year 1 Demand Cost ($)' in df.columns:
            self.year_one_demand_cost = float(df['Year 1 Demand Cost ($)'].values[0])
        if 'Year 1 Payments to Third Party Owner ($)' in df.columns:
            self.year_one_payments_to_third_party_owner = float(df['Year 1 Payments to Third Party Owner ($)'].values[0])
        if 'Total Energy Cost ($)' in df.columns:
            self.total_energy_cost = float(df['Total Energy Cost ($)'].values[0])
        if 'Total Demand Cost ($)' in df.columns:
            self.total_demand_cost = float(df['Total Demand Cost ($)'].values[0])
        if 'Total Payments to Third Party Owner ($)' in df.columns:
            self.total_payments_to_third_party_owner = float(df['Total Payments to Third Party Owner ($)'].values[0])
        if 'Net Capital Costs plus O&M ($)' in df.columns:
            self.net_capital_costs_plus_om = float(df['Net Capital Costs plus O&M ($)'].values[0])
        if 'Total Electricity Exported (kWh)' in df.columns:
            self.year_one_energy_exported = float(df['Total Electricity Exported (kWh)'].values[0])
        if 'Average PV production (kWh)' in df.columns:
            self.average_yearly_pv_energy_produced = float(df['Average PV production (kWh)'].values[0])

    def populate_data_bau(self, df):

        if 'LCC ($)' in df.columns:
            self.lcc_bau = float(df['LCC ($)'].values[0])
        if 'Year 1 Energy Cost ($)' in df.columns:
            self.year_one_energy_cost_bau = float(df['Year 1 Energy Cost ($)'].values[0])
        if 'Year 1 Demand Cost ($)' in df.columns:
            self.year_one_demand_cost_bau = float(df['Year 1 Demand Cost ($)'].values[0])
        if 'Total Energy Cost ($)' in df.columns:
            self.total_energy_cost_bau = float(df['Total Energy Cost ($)'].values[0])
        if 'Total Demand Cost ($)' in df.columns:
            self.total_demand_cost_bau = float(df['Total Demand Cost ($)'].values[0])

    def compute_dispatch(self, df):

        results = dispatch.ProcessOutputs(df, self.path_output, self.file_dispatch, self.year)
        df_xpress = results.get_dispatch()

        if len(df_xpress) > 0:
            if 'Date' in df_xpress.columns:
                dates = (df_xpress['Date'].tolist())
                self.year_one_datetime_start = dates[0]
                self.time_steps_per_hour = int(round(len(dates) / 8760, 0))
                self.zero_array = 8760 * self.time_steps_per_hour * [0]
            if 'Energy Cost ($/kWh)' in df_xpress.columns:
                self.year_one_energy_cost_series = df_xpress['Energy Cost ($/kWh)'].tolist()
            if 'Demand Cost ($/kW)' in df_xpress.columns:
                self.year_one_demand_cost_series = df_xpress['Demand Cost ($/kW)'].tolist()
            if 'Electric load' in df_xpress.columns:
                self.year_one_electric_load_series = (df_xpress['Electric load']).tolist()
            if 'PV to battery' in df_xpress.columns:
                self.year_one_pv_to_battery_series = df_xpress['PV to battery'].tolist()
            if 'PV to load' in df_xpress.columns:
                self.year_one_pv_to_load_series = df_xpress['PV to load'].tolist()
            if 'PV to grid' in df_xpress.columns:
                self.year_one_pv_to_grid_series = df_xpress['PV to grid'].tolist()
            if 'Grid to load' in df_xpress.columns:
                self.year_one_grid_to_load_series = df_xpress['Grid to load'].tolist()
            if 'Grid to battery' in df_xpress.columns:
                self.year_one_grid_to_battery_series = df_xpress['Grid to battery'].tolist()
            if 'State of charge' in df_xpress.columns:
                self.year_one_battery_soc_series = df_xpress['State of charge'].tolist()
            if 'Battery to load' in df_xpress.columns:
                self.year_one_battery_to_load_series = df_xpress['Battery to load'].tolist()
            if 'Battery to grid' in df_xpress.columns:
                self.year_one_battery_to_grid_series = df_xpress['Battery to grid'].tolist()

    def compute_value(self):

        self.npv = self.lcc_bau - self.lcc
        self.year_one_demand_savings = self.year_one_demand_cost_bau - self.year_one_demand_cost
        self.year_one_energy_savings = self.year_one_energy_cost_bau - self.year_one_energy_cost

    def generate_pro_forma(self):

        econ = self.economics
        results = self
        cash_flow = pf.ProForma(self.path_templates, self.path_output, econ, results)
        cash_flow.update_template()
        cash_flow.compute_cashflow()
        self.irr = cash_flow.get_irr()

        """
        d = pf.ProForma(getattr(econ, 'analysis_period'),
                        getattr(econ, 'offtaker_discount_rate_nominal'),
                        getattr(econ, 'offtaker_tax_rate'),
                        getattr(econ, 'pv_macrs_bonus_fraction'),
                        getattr(econ, 'pv_itc_federal'), # modify based on updated incentives
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
                        getattr(econ, 'batt_replacement_cost_kw'),
                        self.year_one_energy_savings,
                        self.year_one_demand_savings,
                        self.year_one_energy_exported,
                        getattr(econ, 'pv_degradation_rate'),
                        self.lcc,
                        self.lcc_bau)

        d.make_pro_forma(self.path_proforma)
        self.irr = d.get_IRR()
        """

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
                    elif v['type'] == datetime:
                        setattr(self, k, value)
                    else:
                        setattr(self, k, v['type'](value))