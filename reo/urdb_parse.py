import json
import os
import operator
import calendar
import numpy
from log_levels import log
from reo.src.dat_file_manager import big_number


class UtilityDatFiles:

    # filenames to use
    name_fuel_rates = 'FuelCost.dat'
    name_demand_periods = 'TimeStepsDemand.dat'
    name_demand_rates = 'DemandRate.dat'
    name_demand_flat_rates = 'DemandRateMonth.dat'
    name_utility_tiers = 'UtilityTiers.dat'
    name_num_ratchets = 'NumRatchets.dat'
    name_export_rates = 'ExportRates.dat'
    name_lookback = 'LookbackMonthsAndPercent.dat'
    name_timesteps_month = 'TimeStepsDemandMonth.dat'
    name_n_tiers = 'bins.dat'
    name_fuel_burn_rate = 'FuelBurnRate.dat'
    name_fuel_rates_base = 'FuelCostBase.dat'
    name_export_rates_base = 'ExportRatesBase.dat'
    name_fuel_burn_rate_base = 'FuelBurnRateBase.dat'
    name_summary = 'Summary.csv'
    name_energy_cost = "energy_cost.txt"
    name_demand_cost = "demand_cost.txt"


    # varnames to use
    var_demand_flat_rates = 'DemandRatesMonth'
    var_demand_rates = 'DemandRates'
    var_demand_periods = 'TimeStepRatchets'
    var_minimum_demand = 'MinDemand'
    var_max_demand_in_tier = 'MaxDemandInTier'
    var_max_usage_in_tier = 'MaxUsageInTier'
    var_fuel_rate = 'FuelRate'
    var_fuel_avail = 'FuelAvail'
    var_num_ratchets = 'NumRatchets'
    var_export_rates = 'ExportRates'
    var_lookback_months = 'DemandLookbackMonths'
    var_lookback_percent = 'DemandLookbackPercent'
    var_timesteps_month = 'TimeStepRatchetsMonth'
    var_n_fuel_tiers = 'FuelBinCount'
    var_n_demand_tiers = 'DemandBinCount'
    var_fuel_burn_rate = 'FuelBurnRateM'

    # fixed data
    TechBase = ['UTIL1']
    Tech = ['PV', 'PVNM', 'UTIL1']
    Load = ['1R', '1W', '1X', '1S']

    def __init__(self, rate_dir, out_dir, out_dir_bau):

        self.path_fuel_rates = os.path.join(rate_dir, self.name_fuel_rates)
        self.path_fuel_rates_base = os.path.join(rate_dir, self.name_fuel_rates_base)
        self.path_demand_periods = os.path.join(rate_dir, self.name_demand_periods)
        self.path_demand_rates = os.path.join(rate_dir, self.name_demand_rates)
        self.path_demand_flat_rates = os.path.join(rate_dir, self.name_demand_flat_rates)
        self.path_utility_tiers = os.path.join(rate_dir, self.name_utility_tiers)
        self.path_num_ratchets = os.path.join(rate_dir, self.name_num_ratchets)
        self.path_export_rates = os.path.join(rate_dir, self.name_export_rates)
        self.path_export_rates_base = os.path.join(rate_dir, self.name_export_rates_base)
        self.path_lookback = os.path.join(rate_dir, self.name_lookback)
        self.path_timesteps_month = os.path.join(rate_dir, self.name_timesteps_month)
        self.path_n_tiers = os.path.join(rate_dir, self.name_n_tiers)
        self.path_fuel_burn_rate = os.path.join(rate_dir, self.name_fuel_burn_rate)
        self.path_fuel_burn_rate_base = os.path.join(rate_dir, self.name_fuel_burn_rate_base)
        self.path_summary = os.path.join(rate_dir, self.name_summary)
        self.path_energy_cost = os.path.join(out_dir, self.name_energy_cost)
        self.path_demand_cost = os.path.join(out_dir, self.name_demand_cost)
        self.path_energy_cost_bau = os.path.join(out_dir_bau, self.name_energy_cost)
        self.path_demand_cost_bau = os.path.join(out_dir_bau, self.name_demand_cost)

        self.data_minimum_demand = 0
        self.data_demand_flat_rates = 12 * [0]
        self.data_demand_rates = []
        self.data_demand_periods = []
        self.data_demand_max_in_bin = 1 * [big_number]
        self.data_usage_max_in_bin = 1 * [big_number]
        self.data_fuel_rate = []
        self.data_fuel_rate_base = []
        self.data_fuel_avail = []
        self.data_fuel_avail_base = []
        self.data_num_ratchets = 12
        self.data_export_rates = []
        self.data_export_rates_base = []
        self.data_lookback_months = []
        self.data_lookback_percent = 0
        self.data_timesteps_month = []
        self.data_n_fuel_tiers = 1
        self.data_n_demand_tiers = 1
        self.data_fuel_burn_rate = []
        self.data_fuel_burn_rate_base = []
        self.data_fuel_rate_summary = []
        self.data_demand_rate_summary = []

        self.has_fixed_demand = "no"
        self.has_tou_demand = "no"
        self.has_demand_tiers = "no"
        self.has_tou_energy = "no"
        self.has_energy_tiers = "no"
        self.max_demand_rate = 0


class RateData:
    # basic header
    utility = []
    rate = []
    sector = []
    label = []
    uri = []
    startdate = []
    enddate = []
    description = []
    usenetmetering = []
    source = []

    # demand charges
    peakkwcapacitymin = []
    peakkwcapacitymax = []
    peakkwcapacityhistory = []

    flatdemandunit = []
    flatdemandstructure = []
    flatdemandmonths = []

    demandrateunit = []
    demandratestructure = []
    demandweekdayschedule = []
    demandweekendschedule = []
    demandratchetpercentage = []
    demandwindow = []
    demandreactivepowercharge = []

    # coincident rates 
    coincidentrateunit = []
    coincidentratestructure = []
    coincidentrateschedule = []

    # energy charges
    peakkwhusagemin = []
    peakkwhusagemax = []
    peakkwhusagehistory = []

    energyratestructure = []
    energyweekdayschedule = []
    energyweekendschedule = []
    energycomments = []

    # other charges
    fixedmonthlycharge = []
    minmonthlycharge = []
    annualmincharge = []



class UrdbParse:

    year = 2018
    is_leap_year = False
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    net_metering = False
    wholesale_rate = 0.0
    excess_rate = 0.0
    cum_days_in_yr = numpy.cumsum(calendar.mdays)
    last_hour_in_month = []
    utility_dat_files = []

    def __init__(self, utility_dats_dir, outputs_dir, outputs_dir_bau, year, time_steps_per_hour=1,
                 net_metering=False, wholesale_rate=0.0, excess_rate=0.0):

        log("INFO", "URDB parse with year: " + str(year) + " net_metering: " + str(net_metering))

        self.year = year
        self.utility_dats_dir = utility_dats_dir
        self.outputs_dir = outputs_dir
        self.outputs_dir_bau = outputs_dir_bau
        self.time_steps_per_hour = time_steps_per_hour
        self.net_metering = net_metering
        self.wholesale_rate = wholesale_rate
        self.excess_rate = excess_rate

        # Count the leap day
        if calendar.isleap(self.year):
            self.is_leap_year = True

        for month in range(0, 12):
            days_elapsed = sum(self.days_in_month[0:month + 1])
            self.last_hour_in_month.append(days_elapsed * 24)

    def parse_all_output(self):
        for utility in os.listdir(self.utility_dats_dir):
            for rate in os.listdir(os.path.join(self.utility_dats_dir, utility)):
                self.parse_specific_rates([utility], [rate])

    def parse_specific_rates(self, utilities, rates):
        log("INFO", "Parsing " + str(len(utilities)) + " rate(s) into: " + self.utility_dats_dir)
        for utility in utilities:
            for rate in rates:
                rate_dir = os.path.join(self.utility_dats_dir, utility, rate)
                self.utility_dat_files = UtilityDatFiles(rate_dir, self.outputs_dir, self.outputs_dir_bau)
                name_file = os.path.join(rate_dir, 'rate_name.txt')
                if os.path.exists(name_file):
                    rate_name = open(name_file, 'r')
                    for filename in os.listdir(rate_dir):
                        if filename == 'json.txt':
                            json_path = os.path.join(rate_dir, filename)

                            with open(json_path, 'r') as json_file:
                                log("INFO", "Processing: " + utility + ", " + rate_name.read())

                                data = json.loads(json_file.read())
                                current_rate = self.parse_rate(data)
                                self.prepare_summary(current_rate)
                                self.prepare_demand_periods(current_rate)
                                self.prepare_energy_costs(current_rate)
                                self.prepare_techs_and_loads_basecase()
                                self.prepare_techs_and_loads()
                                self.write_dat_files()
                                rate_name.close()

    def parse_rate(self, rate):

        # parse header
        current_rate = RateData()
        current_rate.utility = rate['utility']
        current_rate.rate = rate['name']
        current_rate.label = rate['label']

        if 'uri' in rate:
            current_rate.uri = rate['uri']
        if 'sector' in rate:
            current_rate.sector = rate['sector']
        if ('startdate' in rate):
            current_rate.startdate = rate['startdate']
        if ('enddate' in rate):
            current_rate.enddate = rate['enddate']

        if ('description' in rate):
            current_rate.description = rate['description']

        if ('source' in rate):
            current_rate.source = rate['source']

        if ('usenetmetering' in rate):
            current_rate.usenetmetering = rate['usenetmetering']

        # demand charges
        if ('peakkwcapacitymin' in rate):
            current_rate.peakkwcapacitymin = rate['peakkwcapacitymin']
        if ('peakkwcapacitymax' in rate):
            current_rate.peakkwcapacitymax = rate['peakkwcapacitymax']
        if ('peakkwcapacityhistory' in rate):
            current_rate.peakkwcapacityhistory = rate['peakkwcapacityhistory']

        if ('flatdemandunit' in rate):
            current_rate.flatdemandunit = rate['flatdemandunit']
        if ('flatdemandstructure' in rate):
            current_rate.flatdemandstructure = rate['flatdemandstructure']
        if ('flatdemandmonths' in rate):
            current_rate.flatdemandmonths = rate['flatdemandmonths']

        if ('demandrateunit' in rate):
            current_rate.demandrateunit = rate['demandrateunit']
        if ('demandratestructure' in rate):
            current_rate.demandratestructure = rate['demandratestructure']
        if ('demandweekdayschedule' in rate):
            current_rate.demandweekdayschedule = rate['demandweekdayschedule']
        if ('demandweekendschedule' in rate):
            current_rate.demandweekendschedule = rate['demandweekendschedule']
        if ('demandratchetpercentage' in rate):
            current_rate.demandratchetpercentage = rate['demandratchetpercentage']
        if ('demandwindow' in rate):
            current_rate.demandwindow = rate['demandwindow']
        if ('demandreactivepowercharge' in rate):
            current_rate.demandreactivepowercharge = rate['demandreactivepowercharge']

        # energy charges
        if ('peakkwhusagemin' in rate):
            current_rate.peakkwhusagemin = rate['peakkwhusagemin']
        if ('peakkwhusagemax' in rate):
            current_rate.peakkwhusagemax = rate['peakkwhusagemax']
        if ('peakkwhusagehistory' in rate):
            current_rate.peakkwhusagehistory = rate['peakkwhusagehistory']

        if ('energyratestructure' in rate):
            current_rate.energyratestructure = rate['energyratestructure']
        if ('energyweekdayschedule' in rate):
            current_rate.energyweekdayschedule = rate['energyweekdayschedule']
        if ('energyweekendschedule' in rate):
            current_rate.energyweekendschedule = rate['energyweekendschedule']

        if ('energycomments' in rate):
            current_rate.energycomments = rate['energycomments']

            # coincident rates
        if ('coincidentrateunit' in rate):
            current_rate.coincidentrateunit = rate['coincidentrateunit']
        if ('coincidentratestructure' in rate):
            current_rate.coincidentratestructure = rate['coincidentratestructure']
        if ('coincidentrateschedule' in rate):
            current_rate.coincidentrateschedule = rate['coincidentrateschedule']

        # other charges
        if ('fixedmonthlycharge' in rate):
            current_rate.fixedmonthlycharge = rate['fixedmonthlycharge']
        if ('minmonthlycharge' in rate):
            current_rate.minmonthlycharge = rate['minmonthlycharge']
        if ('annualmincharge' in rate):
            current_rate.annualmincharge = rate['annualmincharge']

        return current_rate

    def prepare_summary(self, current_rate):

        if len(current_rate.energyratestructure) > 0:
            if len(current_rate.energyratestructure[0]) > 1:
                self.utility_dat_files.has_energy_tiers = "yes"
            # tou energy only if greater than one period
            if len(current_rate.energyratestructure) > 1:
                self.utility_dat_files.has_tou_energy = "yes"

        if len(current_rate.demandratestructure) > 0:
            if len(current_rate.demandratestructure[0]) > 1:
                self.utility_dat_files.has_demand_tiers = "yes"
            if len(current_rate.energyratestructure) > 1:
                self.utility_dat_files.has_tou_demand = "yes"

        if len(current_rate.flatdemandstructure) > 0:
            self.utility_dat_files.has_fixed_demand = "yes"
            if len(current_rate.flatdemandstructure[0]) > 1:
                self.utility_dat_files.has_demand_tiers = "yes"

        max_demand_rate = 0
        for period in current_rate.demandratestructure:
            for tier in period:
                if 'rate' in tier:
                    rate = tier['rate']
                    if 'adj' in tier:
                        rate += tier['adj']
                    if rate > max_demand_rate:
                        max_demand_rate = rate
        for period in range(0, len(current_rate.flatdemandstructure)):
            for tier in range(0, len(current_rate.flatdemandstructure[period])):
                if 'rate' in current_rate.flatdemandstructure[period][tier]:
                    rate = current_rate.flatdemandstructure[period][tier]['rate']
                    if 'adj' in current_rate.flatdemandstructure[period][tier]:
                        rate += current_rate.flatdemandstructure[period][tier]['adj']
                    if rate > max_demand_rate:
                        max_demand_rate = rate

        self.max_demand_rate = max_demand_rate

    def prepare_energy_costs(self, current_rate):

        n_periods = len(current_rate.energyratestructure)
        if n_periods == 0:
            return

        # parse energy tiers
        energy_tiers = []
        for energy_rate in current_rate.energyratestructure:
            energy_tiers.append(len(energy_rate))

        period_with_max_tiers=energy_tiers.index(max(energy_tiers))
        energy_tier_set = set(energy_tiers)

        if len(energy_tier_set) > 1:
            log("WARNING", "Warning: energy periods contain different numbers of tiers, using limits of period with most tiers")

        self.utility_dat_files.data_n_fuel_tiers = max(energy_tier_set)

        average_rates = False
        rates = []
        rate_average = 0

        # set energy rate tier(bin) limits
        self.utility_dat_files.data_usage_max_in_bin = []

        for energy_tier in current_rate.energyratestructure[period_with_max_tiers]:
            energy_tier_max = big_number

            if 'max' in energy_tier:
                energy_tier_max = energy_tier['max']

            if 'unit' in energy_tier:
                energy_tier_unit = str(energy_tier['unit'])
                # average the prices if we have exotic max usage units
                if energy_tier_unit != 'kWh':
                    average_rates = True

            if 'rate' in energy_tier:
                rates.append(energy_tier['rate']) # only used for kWh/kw pricing
                self.utility_dat_files.data_usage_max_in_bin.append(energy_tier_max) # should be under if 'max'?

        if average_rates:
            rate_average = float(sum(rates)) / max(len(rates), 1)
            self.utility_dat_files.data_n_fuel_tiers = 1
            self.utility_dat_files.data_usage_max_in_bin = []
            self.utility_dat_files.data_usage_max_in_bin.append(big_number)
            log("WARNING", "Cannot handle max usage units of " + energy_tier_unit + "! Using average rate")

        for tier in range(0, self.utility_dat_files.data_n_fuel_tiers): # for each tier
            hour_of_year = 1
            for month in range(0, 12):
                for day in range(0, self.days_in_month[month]):

                    if calendar.weekday(self.year, month + 1, day + 1) < 5:
                        is_weekday = True
                    else:
                        is_weekday = False

                    for hour in range(0, 24):
                        if is_weekday:
                            period = current_rate.energyweekdayschedule[month][hour]
                        else:
                            period = current_rate.energyweekendschedule[month][hour]

                        # workaround for cases where there are different numbers of tiers in periods
                        n_tiers_in_period = len(current_rate.energyratestructure[period])

                        if n_tiers_in_period == 1:
                            tier_use = 0  # use the first and only tier in the period
                        elif tier > n_tiers_in_period-1:  # 'tier' is indexed on zero
                            tier_use = n_tiers_in_period-1  # use last tier in current period, which has less tiers than the maximum tiers for any period
                        else:
                            tier_use = tier

                        if average_rates:
                            rate = rate_average
                        else:
                            rate = current_rate.energyratestructure[period][tier_use]['rate']

                        adj = 0
                        if 'adj' in current_rate.energyratestructure[period][tier_use]:
                            adj = current_rate.energyratestructure[period][tier_use]['adj']

                        for step in range(0, self.time_steps_per_hour):
                            self.utility_dat_files.data_fuel_rate.append(rate + adj)

                        hour_of_year += 1

    def prepare_techs_and_loads_basecase(self):

        zero_array = 8760 * [0]

        # Extract 8760 before modified, NOTE: must be rounded to the same decimal places as energy_costs for zero NPV with no Tech
        self.utility_dat_files.data_fuel_rate_base = [round(x,5) for x in self.utility_dat_files.data_fuel_rate]

        self.utility_dat_files.data_fuel_avail_base = [big_number]

        # Build base case export rate
        tmp_list = []
        for tech in self.utility_dat_files.TechBase:
            for load in self.utility_dat_files.Load:
                tmp_list = operator.add(tmp_list, zero_array)

        self.utility_dat_files.data_export_rates_base = tmp_list

    def prepare_techs_and_loads(self):

        zero_array = 8760 * [0]
        energy_costs = [round(cost, 5) for cost in self.utility_dat_files.data_fuel_rate]

        start_index = len(energy_costs) - 8760 * self.time_steps_per_hour
        self.utility_dat_files.data_fuel_rate_summary = energy_costs[start_index:len(energy_costs)]

        # Assuming ExportRate is the equivalent to the first fuel rate tier:
        negative_energy_costs = [cost * -0.999 for cost in energy_costs[0:8760]]
        negative_wholesale_rate_costs = 8760 * [-1 * self.wholesale_rate]
        negative_excess_rate_costs = 8760 * [-1 * self.excess_rate]

        # FuelRate=array( Tech,FuelBin,TimeStep) is the cost of electricity from each Tech, so 0's for PV, PVNM
        self.utility_dat_files.data_fuel_rate = []

        for i in range(0, len(self.utility_dat_files.Tech) - 1):
            for _ in range(self.utility_dat_files.data_n_fuel_tiers):
                self.utility_dat_files.data_fuel_rate = operator.add(self.utility_dat_files.data_fuel_rate, zero_array)
                self.utility_dat_files.data_fuel_avail.append(0)
        self.utility_dat_files.data_fuel_rate += energy_costs
        self.utility_dat_files.data_fuel_avail.append(big_number)

        # ExportRate is the value of exporting a Tech to the grid under a certain Load bin
        # If there is net metering and no wholesale rate, appears to be zeros for all but 'PV' at '1W'
        tmp_list = []
        for tech in self.utility_dat_files.Tech:
            for load in self.utility_dat_files.Load:
                if tech is 'PV':
                    if load is '1W':
                        if self.net_metering:
                            tmp_list = operator.add(tmp_list, negative_energy_costs)
                        else:
                            tmp_list = operator.add(tmp_list, negative_wholesale_rate_costs)
                    elif load is '1X':
                        tmp_list = operator.add(tmp_list, negative_excess_rate_costs)
                    else:
                        tmp_list = operator.add(tmp_list, zero_array)
                else:
                    tmp_list = operator.add(tmp_list, zero_array)

        self.utility_dat_files.data_export_rates = tmp_list

        #FuelBurnRateM = array(Tech,Load,FuelBin)
        FuelBurnRateM = []
        FuelBurnRateMBase = []
        for tech in self.utility_dat_files.Tech:
            for load in self.utility_dat_files.Load:
                for _ in range(self.utility_dat_files.data_n_fuel_tiers):
                    if tech is 'UTIL1':
                        FuelBurnRateM.append(1)
                        FuelBurnRateMBase.append(1)
                    else:
                        FuelBurnRateM.append(0)
        self.utility_dat_files.data_fuel_burn_rate = FuelBurnRateM
        self.utility_dat_files.data_fuel_burn_rate_base = FuelBurnRateMBase

    def prepare_demand_periods(self, current_rate):

        n_flat = len(current_rate.flatdemandstructure)
        n_tou = len(current_rate.demandratestructure)
        n_rates = n_flat + n_tou

        self.utility_dat_files.data_demand_rate_summary = 8760 * self.time_steps_per_hour * [0]

        if n_rates == 0:
            return
        if n_flat > 0:
            self.prepare_flat_demand(current_rate)
        if n_tou > 0:
            self.prepare_demand_tiers(current_rate, n_tou)
            self.prepare_tou_demand(current_rate)

        self.prepare_demand_rate_summary()

    def prepare_demand_tiers(self, current_rate, n_tou):

        demand_tiers = []
        for demand_rate in current_rate.demandratestructure:
            demand_tiers.append(len(demand_rate))
        demand_tier_set = set(demand_tiers)
        period_with_max_tiers = demand_tiers.index(max(demand_tiers)) #NOTE: this takes the first period if multiple periods have the same number of (max) tiers
        n_tiers = max(demand_tier_set)

        if len(demand_tier_set) > 1:
            log("WARNING", "Warning: multiple lengths of demand tiers, using tiers from the earliest period with the max number of tiers")

            # make the number of tiers the same across all periods by appending on identical tiers
            for r in range(n_tou):
                demand_rate = current_rate.demandratestructure[r]
                demand_rate_new = demand_rate
                n_tiers_in_period = len(demand_rate)
                if n_tiers_in_period != n_tiers:
                    last_tier = demand_rate[n_tiers_in_period - 1]
                    for i in range(0, n_tiers - n_tiers_in_period):
                        demand_rate_new.append(last_tier)
                current_rate.demandratestructure[r] = demand_rate_new

        demand_tiers = {} # for all periods
        demand_maxes = []

        if n_tou > 0:
            self.utility_dat_files.data_demand_max_in_bin = []
            for period in range(n_tou):
                demand_max = []
                for tier in range(n_tiers):
                    demand_tier = current_rate.demandratestructure[period][tier]
                    demand_tier_max = big_number
                    if 'max' in demand_tier:
                        demand_tier_max = demand_tier['max']
                    demand_max.append(demand_tier_max)
                demand_tiers[period] = demand_max
                demand_maxes.append(demand_max[-1])

        # test if the highest tier is the same across all periods
        test_demand_max = set(demand_maxes)
        if len(test_demand_max) > 1:
            log("WARNING", "Warning: highest demand tiers do not match across periods, using max from largest set of tiers")

        self.utility_dat_files.data_demand_max_in_bin = demand_tiers[period_with_max_tiers]

        self.utility_dat_files.data_n_demand_tiers = n_tiers

    def prepare_flat_demand(self, current_rate):

        self.utility_dat_files.data_demand_flat_rates = []
        self.utility_dat_files.data_timesteps_month = [[] for i in range(12)]

        for month in range(12):

            for hour in range(24*self.cum_days_in_yr[month]+1, 24*self.cum_days_in_yr[month+1]+1):
                self.utility_dat_files.data_timesteps_month[month].append(hour)

            period = 0
            for flat in current_rate.flatdemandstructure:
                flat_rate = 0
                flat_adj = 0

                if 'rate' in flat[0]:
                    flat_rate = flat[0]['rate']

                if 'adj' in flat[0]:
                    flat_adj = flat[0]['adj']

                if len(current_rate.flatdemandmonths) > 0:
                    period_in_month = current_rate.flatdemandmonths[month]

                    if period_in_month == period:
                        self.utility_dat_files.data_demand_flat_rates.append(flat_rate + flat_adj)

                else:
                    self.utility_dat_files.data_demand_flat_rates.append(flat_rate + flat_adj)

                period += 1

    def prepare_demand_rate_summary(self):

        for month in range(12):
            flat_rate = self.utility_dat_files.data_demand_flat_rates[month]
            month_hours = self.get_hours_in_month(month)

            for hour in month_hours:
                self.utility_dat_files.data_demand_rate_summary[hour] += flat_rate

    def prepare_tou_demand(self, current_rate):

        demand_periods = []
        demand_rates = []

        if type(current_rate.peakkwcapacitymin) is int:
            self.utility_dat_files.data_minimum_demand = current_rate.peakkwcapacitymin

        self.utility_dat_files.demand_rates = []
        for month in range(12):

            for demand_period in range(len(current_rate.demandratestructure)):

                time_steps = self.get_tou_steps(current_rate, month, demand_period)

                if len(time_steps) > 0:

                    demand_periods.append(time_steps)

                    for tier in current_rate.demandratestructure[demand_period]:

                        tou_rate = tier['rate']
                        tou_adj = 0

                        if 'adj' in tier:
                            tou_adj = tier['adj']

                        demand_rates.append(tou_rate + tou_adj)

                        for step in time_steps:
                            self.utility_dat_files.data_demand_rate_summary[step - 1] += tou_rate + tou_adj

        self.utility_dat_files.data_demand_periods = demand_periods
        self.utility_dat_files.data_demand_rates = demand_rates
        self.utility_dat_files.data_num_ratchets = len(demand_periods)

    def write_dat_files(self):

        # flat demand
        file_path = open(self.utility_dat_files.path_demand_flat_rates, 'w')
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_demand_flat_rates,
                                   self.utility_dat_files.data_demand_flat_rates)
        file_path.close()

        # tou demand (minimum demand and rates
        file_path = open(self.utility_dat_files.path_demand_rates, 'w')
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_minimum_demand,
                                   self.utility_dat_files.data_minimum_demand)
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_demand_rates,
                                   self.utility_dat_files.data_demand_rates)
        file_path.close()
        file_path = open(self.utility_dat_files.path_demand_periods, 'w')
        self.write_list_of_lists(file_path,
                                 self.utility_dat_files.var_demand_periods,
                                 self.utility_dat_files.data_demand_periods)
        file_path.close()

        # num ratchets
        file_path = open(self.utility_dat_files.path_num_ratchets, 'w')
        self.write_variable_equals(file_path,
                                   self.utility_dat_files.var_num_ratchets,
                                   self.utility_dat_files.data_num_ratchets)
        file_path.close()

        # utility tiers
        file_path = open(self.utility_dat_files.path_utility_tiers, 'w')
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_max_demand_in_tier,
                                   self.utility_dat_files.data_demand_max_in_bin)
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_max_usage_in_tier,
                                   self.utility_dat_files.data_usage_max_in_bin)
        file_path.close()

        # fuel rate
        file_path = open(self.utility_dat_files.path_fuel_rates, 'w')
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_fuel_rate,
                                   self.utility_dat_files.data_fuel_rate)
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_fuel_avail,
                                   self.utility_dat_files.data_fuel_avail)
        file_path.close()

        # fuel rate base case
        file_path = open(self.utility_dat_files.path_fuel_rates_base, 'w')
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_fuel_rate,
                                   self.utility_dat_files.data_fuel_rate_base)
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_fuel_avail,
                                   self.utility_dat_files.data_fuel_avail_base)
        file_path.close()

        # export rate
        file_path = open(self.utility_dat_files.path_export_rates, 'w')
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_export_rates,
                                   self.utility_dat_files.data_export_rates)
        file_path.close()

        # export rate base case
        file_path = open(self.utility_dat_files.path_export_rates_base, 'w')
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_export_rates,
                                   self.utility_dat_files.data_export_rates_base)
        file_path.close()

        # lookback months and percent
        file_path = open(self.utility_dat_files.path_lookback, 'w')
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_lookback_months,
                                   self.utility_dat_files.data_lookback_months)
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_lookback_percent,
                                   self.utility_dat_files.data_lookback_percent)
        file_path.close()

        # timestep ratchets month
        file_path = open(self.utility_dat_files.path_timesteps_month, 'w')
        self.write_list_of_lists(file_path,
                                   self.utility_dat_files.var_timesteps_month,
                                   self.utility_dat_files.data_timesteps_month)
        file_path.close()

        # bins/tiers
        file_path = open(self.utility_dat_files.path_n_tiers, 'w')
        self.write_variable_equals(file_path,
                                   self.utility_dat_files.var_n_fuel_tiers,
                                   self.utility_dat_files.data_n_fuel_tiers)
        self.write_variable_equals(file_path,
                                   self.utility_dat_files.var_n_demand_tiers,
                                   self.utility_dat_files.data_n_demand_tiers)
        file_path.close()

        # fuel burn rate
        file_path = open(self.utility_dat_files.path_fuel_burn_rate, 'w')
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_fuel_burn_rate,
                                   self.utility_dat_files.data_fuel_burn_rate)
        file_path.close()

        # fuel burn rate base
        file_path = open(self.utility_dat_files.path_fuel_burn_rate_base, 'w')
        self.write_single_variable(file_path,
                                   self.utility_dat_files.var_fuel_burn_rate,
                                   self.utility_dat_files.data_fuel_burn_rate_base)
        file_path.close()

        # summary
        file_path = open(self.utility_dat_files.path_summary, 'w')
        self.write_summary(file_path)
        file_path.close()

        # hourly cost summary
        self.write_energy_cost(self.utility_dat_files.path_energy_cost)
        self.write_demand_cost(self.utility_dat_files.path_demand_cost)
        self.write_energy_cost(self.utility_dat_files.path_energy_cost_bau)
        self.write_demand_cost(self.utility_dat_files.path_demand_cost_bau)

    def write_summary(self, file_name):
        file_name.write('Fixed Demand,TOU Demand,Demand Tiers,TOU Energy,Energy Tiers,Max Demand Rate ($/kW)\n')
        file_name.write(self.utility_dat_files.has_fixed_demand + ',' +
                        self.utility_dat_files.has_tou_demand + ',' +
                        self.utility_dat_files.has_demand_tiers + ',' +
                        self.utility_dat_files.has_tou_energy + ',' +
                        self.utility_dat_files.has_energy_tiers + ',' +
                        str(self.max_demand_rate)
                        )

    def write_energy_cost(self, file_path):

        with open(file_path, 'wb') as f:
            for v in self.utility_dat_files.data_fuel_rate_summary:
                f.write(str(v)+'\n')

    def write_demand_cost(self, file_path):

        with open(file_path, 'wb') as f:
            for v in self.utility_dat_files.data_demand_rate_summary:
                f.write(str(v)+'\n')

    @staticmethod
    def write_single_variable(file_name, var_name, array):
        file_name.write(var_name + ': [\n')

        if type(array) is int:
            file_name.write(str(array) + '\n')
        else:
            for val in array:
                file_name.write(str(val) + '\n')

        file_name.write(']\n')

    @staticmethod
    def write_list_of_lists(file_name, var_name, lol):
        file_name.write(var_name + ': [\n')

        for i in range(0, len(lol)):
            file_name.write('[')
            for j in lol[i]:
                file_name.write(str(j) + ' ')
            file_name.write(']\n')

        file_name.write(']\n')

    @staticmethod
    def write_variable_equals(file_name, var_name, data):
        file_name.write(var_name + '=' + str(data) + '\n')

    def get_hours_in_month(self, month):

        hours = []
        hours.append(0)
        for m in range(12):
            hours_previous = hours[m]
            days_in_month = calendar.monthrange(self.year, m + 1)[1]
            # no leap days allowed
            if m == 1 and calendar.isleap(self.year):
                days_in_month -= 1
            hours.append(24 * days_in_month + hours_previous)

        return range(hours[month], hours[month + 1])

    def get_tou_steps(self, current_rate, month, period):
        step_array = []
        start_step = 1
        start_hour = 1

        if month > 0:
            start_hour = self.last_hour_in_month[month - 1] + 1
            start_step = (self.last_hour_in_month[month - 1] + 1) * self.time_steps_per_hour

        hour_of_year = start_hour
        step_of_year = start_step
        for day in range(0, self.days_in_month[month]):

            if calendar.weekday(self.year, month + 1, day + 1) < 5:
                is_weekday = True
            else:
                is_weekday = False

            for hour in range(0, 24):
                for step in range(0, self.time_steps_per_hour):
                    if is_weekday and current_rate.demandweekdayschedule[month][hour] == period:
                        step_array.append(step_of_year)
                    elif not is_weekday and current_rate.demandweekendschedule[month][hour] == period:
                        step_array.append(step_of_year)
                    step_of_year += 1
                hour_of_year += 1

        return step_array

