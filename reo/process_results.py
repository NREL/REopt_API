import os
import pandas as pd
import csv
import dispatch
import pro_forma
import openpyxl
import sys
from RunScenarios.logger import log


class ProcessResults:

    runs = []

    # summary dataframe
    df_results_base = []
    df_results = []
    df_rate_summary = []
    df_economics = []

    header = []
    header_base = []

    data = []
    data_base = []

    # Xpress/output absolute path
    output_path = []
    path_dat_library = []
    path_scenarios = []

    file_summary = 'summary.csv'
    file_demand = 'DemandHourly.csv'
    file_rate_criteria = 'rate_criteria.csv'
    file_economic_inputs = 'economic_inputs.csv'
    resultsCSV = 'results.csv'
    resultsCSV_base = 'base_results.csv'
    file_reo_results = 'REOresults.csv'

    # results column order
    output_columns = ['City',
                      'Utility',
                      'Rate',
                      'Fixed Demand',
                      'TOU Demand',
                      'Demand Tiers',
                      'TOU Energy',
                      'Energy Tiers',
                      'Max Demand Rate ($/kW)',
                      'Building Type',
                      'Load Standard Deviation (kW)',
                      'Load Mean (kW)',
                      'Load Annual (kWh)',
                      'Peak Annual Demand (kW)',
                      'Average Monthly Peak Demand (kW)',
                      'PV Size (kW)',
                      'Battery Capacity (kWh)',
                      'Battery Power (kW)',
                      'LCC ($)',
                      'LCC BAU ($)',
                      'NPV ($)',
                      'IRR (%)',
                      'Capital Cost ($)',
                      'Total kWh Cost ($)',
                      'Total kWh Cost BAU ($)',
                      'Total kWh Savings ($)',
                      'Total Demand Cost ($)',
                      'Total Demand Cost BAU ($)',
                      'Total Demand Savings ($)',
                      'Year 1 Energy Cost ($)',
                      'Year 1 Energy Cost BAU ($)',
                      'Year 1 Demand Cost ($)',
                      'Year 1 Demand Cost BAU ($)',
                      'Total PV production (kWh)',
                      'Optimization Time (s)']

    def __init__(self, runs, project_path, output_path):
        """
        :param runs: list of scenario names
        :param project_path: 
        :param output_path:  
        """
        self.output_path = output_path
        self.path_dat_library = os.path.join(project_path, 'DatLibrary')
        self.path_scenarios = os.path.join(project_path, 'RunScenarios')

        # check if all runs are complete, remove if not
        finished_runs = []
        for run in runs:
            if 'REOresults.csv' in os.listdir(os.path.join(output_path, run)):
                finished_runs.append(run)
            else:
                log_string = "{} not done. Removed from results.".format(run)
                print log_string
                log.info(log_string)

        optimum_runs = []
        for run in finished_runs:
            if self.is_optimum(run):
                optimum_runs.append(run)
            else:
                log_string = "{} is not optimum. Removed from results.".format(run)
                print log_string
                log.info(log_string)

        if len(optimum_runs) == 0:
            log.warn("No runs were optimal.")
            sys.exit("No runs were optimal.")
        else:
            self.runs = optimum_runs

    def is_optimum(self, run):

        path_reo_results = os.path.join(self.output_path, run, self.file_reo_results)

        df = pd.read_csv(path_reo_results, names=['Random', 'Tech', 'Size'], header=None)
        df_status = df.loc[df['Random'] == 'Problem status']
        return_code = df_status['Tech'][0].strip()
        optimum = 'Optimum found'

        return return_code == optimum

    def prepare_summary(self):

        for run in self.runs:
            self.load_summaryCSV(run)
            self.load_summaryCSV_base(run)

        self.df_results = pd.DataFrame(self.data, columns=self.header, index=self.runs)
        self.df_results_base = pd.DataFrame(self.data_base, columns=self.header_base, index=self.runs)

        self.process_load_profile()

        resultsCSV = os.path.join(self.output_path, self.resultsCSV)
        resultsCSV_base = os.path.join(self.output_path, self.resultsCSV_base)

        # have to do this to get LCCs in numeric format correctly (hack)
        self.df_results.to_csv(resultsCSV)
        self.df_results_base.to_csv(resultsCSV_base)

        self.merge_results(resultsCSV_base)
        self.compute_savings()
        self.compute_npv(resultsCSV, resultsCSV_base)
        self.load_rate_summary()
        self.screen_utility_rates() # this method possible removes runs from self.runs

        for run in self.runs:
            self.load_economics(run)

        self.generate_pro_forma()
        self.return_irr()
        self.output_dispatch()

        self.finalize(resultsCSV, resultsCSV_base)
        log.info("proccess_results complete.")

    def load_rate_summary(self):

        utility = self.df_results['Utility'].tolist()
        rate = self.df_results['Rate'].tolist()

        cur_dir = os.getcwd()
        rate_path = os.path.join(self.path_dat_library, 'Utility')
        os.chdir(rate_path)

        df_rate_summary = pd.DataFrame()
        for i, run in enumerate(self.runs):
            file_name = os.path.join(utility[i], rate[i], 'Summary.csv')
            rate_summary = pd.read_csv(file_name)
            df_rate_summary = df_rate_summary.append(rate_summary)

        df_rate_summary = df_rate_summary.set_index(self.df_results.index)
        results = pd.concat([self.df_results, df_rate_summary], axis=1)
        self.df_results = results
        os.chdir(cur_dir)

    def load_summaryCSV(self, run):
        path_summary = os.path.join(self.output_path, run)

        write_header = False
        if len(self.header) == 0:
            write_header = True
        data = []
        pv_size = 0
        pv_indicies = []
        summary_file = os.path.join(path_summary, self.file_summary)

        ind = 0
        with open(summary_file, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:

                if row[0] == 'PV Size (kW)' or row[0] == 'PVNM Size (kW)':
                    pv_size += float(row[1])
                    pv_indicies.append(ind)
                    continue
                if write_header:
                    self.header.append(row[0])
                data.append(row[1])
                ind += 1
        if write_header:
            self.header.append('PV Size (kW)')
        data.append(pv_size)
        self.data.append(data)

    def load_summaryCSV_base(self, run):
        path_summary = os.path.join(self.output_path, run, 'base')

        write_header = False
        if len(self.header_base) == 0:
            write_header = True
        data = []
        summary_file = os.path.join(path_summary, self.file_summary)
        with open(summary_file, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if write_header:
                    self.header_base.append(row[0])
                data.append(row[1])
        self.data_base.append(data)

    def load_economics(self, run):
        path_economics = os.path.join(self.output_path, run)
        df_economics = pd.read_csv(os.path.join(path_economics, self.file_economic_inputs), index_col=0)
        df_economics = df_economics.transpose()
        df_economics['Run'] = run
        df_economics.set_index(['Run'], inplace=True)

        if len(self.df_economics) > 0:
            self.df_economics = pd.concat([self.df_economics, df_economics])
        else:
            self.df_economics = df_economics

    def generate_pro_forma(self):
        '''
        default ProForma assumes base case economics (see __init__ arguments below):

        def __init__(self, discount_rate=0.08, tax_rate=0.35, bonus_fraction=0.5, itc_fraction=0.3, elec_escalation=0.0039, \
                     inflation=0.02, om_cost=20, pv_cost=2160, batt_cost=500, invt_cost=1600, batt_repl=200)

        dcf(path_file, scenario_num='X', pv_size=0, batt_capacity=0, batt_power=0, energy_savings_yr1=0, demand_savings_yr1=0)
        '''
        df = self.df_results
        econ = self.df_economics
        for i, run in enumerate(self.runs):

            d = pro_forma.ProForma(econ.iloc[i]['analysis_period'],
                                   econ.iloc[i]['r_nominal_offtaker'],
                                   econ.iloc[i]['r_tax_offtaker'],
                                   econ.iloc[i]['bonus_fraction'],
                                   econ.iloc[i]['r_ITC'],
                                   econ.iloc[i]['r_nominal_escalation'],
                                   econ.iloc[i]['r_inflation'],
                                   econ.iloc[i]['pv_om'],
                                   econ.iloc[i]['pv_price'],
                                   econ.iloc[i]['batt_price_kWh'],
                                   econ.iloc[i]['batt_price_kW'],
                                   econ.iloc[i]['batt_replacement_price_kWh'])

            results_folder = os.path.join(self.output_path, run)
            d.dcf(results_folder, run,
                  df.iloc[i]['PV Size (kW)'],
                  df.iloc[i]['Battery Capacity (kWh)'],
                  df.iloc[i]['Battery Power (kW)'],
                  float(df.iloc[i]['Year 1 Energy Cost BAU ($)']) - float(df.iloc[i]['Year 1 Energy Cost ($)']),
                  float(df.iloc[i]['Year 1 Demand Cost BAU ($)']) - float(df.iloc[i]['Year 1 Demand Cost ($)']))

    def return_irr(self):

        irr = []
        for run in self.runs:
            # need absolute path
            path_output_absolute = os.path.join(os.getcwd(), "Xpress", "output")
            results_folder = os.path.join(path_output_absolute, run)
            file_proforma = os.path.join(results_folder, "ProForma_" + run + ".xlsx")

            # grab IRR
            wb = openpyxl.load_workbook(file_proforma, data_only=True)
            sheet = wb["Cash Flow"]
            irr.append(sheet["B39"].value * 100)

        self.df_results.loc[:, 'IRR (%)'] = pd.Series(irr, index=self.df_results.index)

    def process_load_profile(self):
        building_types = []
        cities = []
        stdev = []
        mean = []
        size = []
        peak_annual_demand = []
        average_monthly_peak_demand = []

        load_profiles = []
        for run in self.runs:
            with open(os.path.join(self.output_path, run, 'Go.bat')) as f:
                cmdline = f.readline()
            cmdline = cmdline[cmdline.index('Load8760'):]
            load_name = cmdline[0:cmdline.index("'")]
            load_profiles.append(load_name)

        count = 1
        for line in load_profiles:
            if count > len(self.runs):
                break
            last_underscore = 0
            last_dot = 0
            index = 0
            underscores = []
            for char in line:
                if char == '_':
                    last_underscore = index
                    underscores.append(last_underscore)
                if char == '.':
                    last_dot = index
                index += 1
            building = line[(last_underscore + 1):last_dot]
            building_types.append(building)

            # get load information
            city = line[(underscores[1]+1):underscores[2]]
            cities.append(city)

            path_info_file = os.path.join(self.path_dat_library, 'LoadInfo', 'LoadInfo_' + city + '_' + building + '.csv')
            df_info = pd.read_csv(path_info_file, index_col=False, dtype=float)

            stdev.append(df_info.loc[0, 'Load Standard Deviation (kW)'])
            mean.append(df_info.loc[0, 'Load Mean (kW)'])
            size.append(df_info.loc[0, 'Load Annual (kWh)'])
            peak_annual_demand.append(df_info.loc[0, 'Peak Annual Demand (kW)'])
            average_monthly_peak_demand.append(df_info.loc[0, 'Average Monthly Peak Demand (kW)'])

            count += 1

        self.df_results.loc[:, 'Building Type'] = pd.Series(building_types, index=self.df_results.index)
        self.df_results.loc[:, 'Load Standard Deviation (kW)'] = pd.Series(stdev, index=self.df_results.index)
        self.df_results.loc[:, 'Load Mean (kW)'] = pd.Series(mean, index=self.df_results.index)
        self.df_results.loc[:, 'Load Annual (kWh)'] = pd.Series(size, index=self.df_results.index)
        self.df_results.loc[:, 'Peak Annual Demand (kW)'] = pd.Series(peak_annual_demand, index=self.df_results.index)
        self.df_results.loc[:, 'Average Monthly Peak Demand (kW)'] = pd.Series(average_monthly_peak_demand, index=self.df_results.index)
        self.df_results.loc[:, 'City'] = pd.Series(cities, index=self.df_results.index)

    def merge_results(self, resultsCSV_base):

        base_costs = pd.read_csv(resultsCSV_base, usecols=['LCC ($)', 'Total kWh Cost ($)', 'Total Demand Cost ($)',
                                                     'Year 1 Energy Cost ($)', 'Year 1 Demand Cost ($)'])

        base_costs.columns = ['LCC BAU ($)', 'Total kWh Cost BAU ($)', 'Total Demand Cost BAU ($)',
                              'Year 1 Energy Cost BAU ($)', 'Year 1 Demand Cost BAU ($)']
        base_costs.index = self.df_results.index
        results = pd.concat([self.df_results, base_costs], axis=1)

        self.df_results = results

    def compute_savings(self):

        self.df_results['Total Demand Cost ($)'] = self.df_results['Total Demand Cost ($)'].apply(pd.to_numeric)
        self.df_results['Total kWh Cost ($)'] = self.df_results['Total kWh Cost ($)'].apply(pd.to_numeric)

        self.df_results['Total Demand Savings ($)'] = pd.Series(self.df_results['Total Demand Cost BAU ($)'] -
                                                                self.df_results['Total Demand Cost ($)'],
                                                                index=self.df_results.index)

        self.df_results['Total kWh Savings ($)'] = pd.Series(self.df_results['Total kWh Cost BAU ($)'] -
                                                             self.df_results['Total kWh Cost ($)'],
                                                             index=self.df_results.index)

    def compute_npv(self, resultsCSV, resultsCSV_base):
        # hack to get datatypes working
        lcc = pd.read_csv(resultsCSV, usecols=['LCC ($)'])
        lcc_base = pd.read_csv(resultsCSV_base, usecols=['LCC ($)'])
        npv = lcc_base.subtract(lcc)
        npv.columns = ['NPV ($)']
        npv.index = self.df_results.index

        results = pd.concat([self.df_results, npv], axis=1)
        self.df_results = results

    def screen_utility_rates(self):

        file_rate_criteria = os.path.join(self.path_scenarios, 'input', self.file_rate_criteria)
        remove_list = []

        for scenario, row in self.df_results.iterrows():
            utility = row['Utility']
            rate = row['Rate']
            peak_demand = float(row['Peak Annual Demand (kW)'])
            monthly_energy = float(row['Load Annual (kWh)'])/12

            remove = True

            with open(file_rate_criteria, 'r') as f_rate:
                rate_reader = csv.reader(f_rate)

                for line in rate_reader:
                    util_check = line[0]
                    rate_check = line[1]
                    rate_check = rate_check.replace(' ', '_').replace(':', '').replace(',', '')

                    if util_check == utility and rate_check == rate:

                        min_demand = line[2]
                        max_demand = line[3]
                        min_energy = line[4]
                        max_energy = line[5]

                        if min_demand == "none" or peak_demand > float(min_demand):
                            if max_demand == "none" or peak_demand < float(max_demand):
                                if min_energy == "none" or monthly_energy > float(min_energy):
                                    if max_energy == "none" or monthly_energy < float(max_energy):
                                        remove = False
                        break

            if remove is True:
                log_string = "Removed " + scenario + " utility: " + util_check + " rate: " + rate_check
                print log_string
                log.info(log_string)
                remove_list.append(scenario)

        self.df_results.drop(remove_list, inplace=True)
        for s in remove_list:
            self.runs.remove(s)

    def output_dispatch(self):

        for run in self.runs:
            results_folder = os.path.join(self.output_path, run)
            outputs = dispatch.ProcessOutputs(results_folder, results_folder, 2017, 1, run)

            # specify 'save' or 'show'.  'save outputs .png in data_root
            # for day in range(1, 31):
            #    outputs.plot_dispatch(2015, 7, day, 'save')

    def finalize(self, resultsCSV, resultsCSV_base):

        os.remove(resultsCSV_base)
        self.df_results = self.df_results[self.output_columns]
        self.df_results.to_csv(resultsCSV)
