import re
from reo.log_levels import log
from reo.src.dat_file_manager import DatFileManager
from reo.src.urdb_parse import UrdbParse


class ElecTariff(object):

    def __init__(self, run_id, paths, urdb_rate, blended_utility_rate, demand_charge, net_metering_limit,
                 load_year, wholesale_rate, time_steps_per_hour,
                 **kwargs):

        self.run_id = run_id
        self.wholesale_rate = wholesale_rate
        self.time_steps_per_hour = time_steps_per_hour
        self.load_year = load_year

        self.net_metering = False
        if net_metering_limit > 0:
            self.net_metering = True

        if urdb_rate is not None:
            log("INFO", "Parsing URDB rate")
        
        elif None not in [blended_utility_rate, demand_charge]:
                log("INFO", "Making URDB rate from blended data")
                urdb_rate = self.make_urdb_rate(blended_utility_rate, demand_charge)
        else:
            raise ValueError("urdb_rate or [blended_utility_rate, demand_charge] are required inputs")

        self.utility_name = re.sub(r'\W+', '', str(urdb_rate.get('utility')))
        self.rate_name = re.sub(r'\W+', '', str(urdb_rate.get('name')))
        self.urdb_rate = urdb_rate

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
