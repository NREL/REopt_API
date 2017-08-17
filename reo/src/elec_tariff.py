import re
from collections import namedtuple

from reo.log_levels import log
from reo.src.dat_file_manager import DatFileManager
from reo.src.urdb_parse import UrdbParse


class REoptElecTariff(object):
    """
    uses a URDB formatted JSON (python dict) to create REopt input parameters
    """

    def __init__(self, urdb_rate):
        """
        demand_rates_monthly (monthly)  'DemandRatesMonth'  - list of floats, length = 12
        demand_ratchets_monthly  'TimeStepRatchetsMonth'  - list of 12 lists, containing integers for timesteps in each month
        demand_rates_tou  'DemandRates'   - list of demand rates, length = demand_num_ratchets_tou
        demand_ratchets_tou  'TimeStepRatchets'  - list of lists, containing integers for timesteps in each TOU ratchet
        demand_num_ratchets_tou  'NumRatchets' - int, number of TOU ratchets
        demand_tiers_num  'DemandBinCount'  - int, number of demand tiers
        demand_max_in_tiers  'MaxDemandInTier'  - list of floats, max demand for each demand tier (referred to 'bins' in REopt)
        demand_lookback_months  'DemandLookbackMonths'  - list of 1's and 0's, length = 12, 1's indicate months that facility demand charge applies to
        demand_lookback_percent  'DemandLookbackPercent'  - float, percent of the peak demand over the lookback months that facility demand charge applies to

        energy_rates  'FuelRate' - list of floats, US$/kWh cost of energy at each time step
        energy_tiers_num  'FuelBinCount' - int, number of energy tiers
        energy_max_in_tiers  'MaxUsageInTier' - list of floats, max energy for each energy tier (referred to 'bins' in REopt)

        export_rates  'ExportRates' - list of floats, US$/kWh rate at which a Tech can export energy to the grid
        energy_burn_rate  'FuelBurnRateM' - list of floats, fuel burn rate of each Tech (currently 1's and 0's)

        NOT USED IN REopt:
            energy_avail  'FuelAvail' - list of floats, amount of energy available from each Tech (UTIL1 is set to big_number)
            demand_min  'MinDemand'  - int (kW)

        """

        UtilArg = namedtuple('util_arg', "REopt_name type units required_length array_of")

        energy_rates = UtilArg('FuelRate', 'list of floats', 'US$/kWh', 'energy_tiers_num, timesteps',
                               'Tech, FuelBin, TimeStep')


class ElecTariff(REoptElecTariff):

    def __init__(self, run_id, dat_lib, urdb_rate, blended_utility_rate, demand_charge, net_metering_limit,
                 load_year,
                 **kwargs):

        self.run_id = run_id

        net_metering = False
        if net_metering_limit > 0:
            net_metering = True

        if urdb_rate is not None:
            log("INFO", "Parsing URDB rate")
        elif None not in [blended_utility_rate, demand_charge]:
                log("INFO", "Making URDB rate from blended data")
                urdb_rate = self.make_urdb_rate(blended_utility_rate, demand_charge)
        else:
            raise ValueError("urdb_rate or [blended_utility_rate, demand_charge] are required inputs")

        self.utility_name = re.sub(r'\W+', '', urdb_rate.get('utility'))
        self.rate_name = re.sub(r'\W+', '', urdb_rate.get('name'))

        parser = UrdbParse(urdb_rate=urdb_rate, paths=dat_lib.paths, year=load_year,
                           time_steps_per_hour=dat_lib.time_steps_per_hour,
                           net_metering=net_metering, wholesale_rate=dat_lib.wholesale_rate)
        parser.parse_rate(self.utility_name, self.rate_name)

        super(ElecTariff, self).__init__(urdb_rate)
        DatFileManager().add_elec_tariff(self)

    def make_urdb_rate(self, blended_utility_rate, demand_charge):

        urdb_rate = {}

        # energy rate
        energyratestructure = []
        energyweekdayschedule = []
        energyweekendschedule = []

        flatdemandstructure = []
        flatdemandmonths = []

        unique_energy_rates = set(blended_utility_rate)
        unique_demand_rates = set(demand_charge)

        for energy_rate in unique_energy_rates:
            rate = [{'rate': energy_rate, 'unit': 'kWh'}]
            energyratestructure.append(rate)

        for demand_rate in unique_demand_rates:
            rate = [{'rate': demand_rate}]
            flatdemandstructure.append(rate)

        for month in range(0, 12):
            energy_period = 0
            demand_period = 0
            for energy_rate in unique_energy_rates:
                if energy_rate == blended_utility_rate[month]:
                    tmp = [energy_period] * 24
                    energyweekdayschedule.append(tmp)
                    energyweekendschedule.append(tmp)
                energy_period += 1
            for demand_rate in unique_demand_rates:
                if demand_rate == demand_charge[month]:
                    flatdemandmonths.append(demand_period)
                demand_period += 1

        # ouput
        urdb_rate['energyweekdayschedule'] = energyweekdayschedule
        urdb_rate['energyweekendschedule'] = energyweekendschedule
        urdb_rate['energyratestructure'] = energyratestructure
        urdb_rate['utility'] = 'user rate'
        urdb_rate['name'] = 'user rate'

        if sum(unique_demand_rates) > 0:
            urdb_rate['flatdemandstructure'] = flatdemandstructure
            urdb_rate['flatdemandmonths'] = flatdemandmonths
            urdb_rate['flatdemandunit'] = 'kW'

        urdb_rate['label'] = self.run_id
        urdb_rate['name'] = "Custom_rate_" + str(self.run_id)
        urdb_rate['utility'] = "Custom_utility_" + str(self.run_id)
        return urdb_rate