from reo.src.dat_file_manager import big_number


class IncentiveProvider(object):

    def __init__(self, name, incentives_dict):
        """

        :param name: str, either 'total', 'federal', 'state', or 'utility'
        :param incentives_dict: dict of POST params, filtered by 'pv' or 'batt'

        NOTE: future POST structure will not require filtering by 'pv' or 'batt'
        """

        # ITC only applies to federal, since don't track other tax rates
        if name == 'federal' or name == 'total':
            self.itc = incentives_dict.get('itc_' + name)

            # Set maxes to 0 if there is no incentive (critical for cap cost calculation)
            self.itc_max = 0
            if self.itc > 0:
                self.itc_max = incentives_dict.get('itc_' + name + '_max') or big_number

        else: # region == 'state' or region == 'utility'
            self.ibi = incentives_dict.get('ibi_' + name)
            self.ibi_max = 0
            if self.ibi > 0:
                self.ibi_max = incentives_dict.get('ibi_' + name + '_max') or big_number

        self.rebate = incentives_dict.get('rebate_' + name)   # $/kW
        self.rebate_max = 0
        if self.rebate > 0:
            self.rebate_max = incentives_dict.get('rebate_' + name + '_max') or big_number



class ProductionBasedIncentive(object):

    def __init__(self, pbi=None, pbi_max=big_number, pbi_years=big_number, pbi_system_max=big_number, **kwargs):

        self.us_dollars_per_kw = pbi
        self.max_us_dollars_per_kw = pbi_max
        self.years = pbi_years
        self.max_kw = pbi_system_max


class Incentives(object):
    """
    high level incentives object for attaching to production technologies and storage
    """
    macrs_five_year = [0.2, 0.32, 0.192, 0.1152, 0.1152, 0.0576]  # IRS pub 946
    macrs_seven_year = [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446]

    def __init__(self, POST, tech=None, macrs_years=5, macrs_bonus_fraction=0.5, macrs_itc_reduction=0.5,
                 include_production_based=False):

        self.macrs_bonus_fraction = macrs_bonus_fraction
        self.macrs_itc_reduction = macrs_itc_reduction

        if macrs_years == 5:
            self.macrs_schedule = Incentives.macrs_five_year
        elif macrs_years == 7:
            self.macrs_schedule = Incentives.macrs_seven_year
        elif macrs_years == 0:
            self.macrs_bonus_fraction = 0
            self.macrs_itc_reduction = 0
            self.macrs_schedule = [0]
        else:
            raise ValueError("macrs_years must be 0, 5 or 7.")

        if tech:  # not needed once we modify POST dict
            filtered_kwargs = self._filter_inputs(tech, POST)
        else:
            filtered_kwargs = POST

        # the "total" incentive used by storage, since not a standard TECH
        self.total = IncentiveProvider('total', incentives_dict=filtered_kwargs)
        self.federal = IncentiveProvider('federal', incentives_dict=filtered_kwargs)
        self.state = IncentiveProvider('state', incentives_dict=filtered_kwargs)
        self.utility = IncentiveProvider('utility', incentives_dict=filtered_kwargs)

        if include_production_based:
            self.production_based = ProductionBasedIncentive(**filtered_kwargs)
        else:
            self.production_based = None

    def _filter_inputs(self, tech, POST):
        """
        find all keys in POST that begin with tech+'_' and returns a dict with the same
        key value pairs that start with tech+'_', except tech+'_' is removed from keys
        :param tech: str, 'pv' or 'batt'
        :param POST: POST dictionary
        :return:
        """
        return dict((k[len(tech.lower() + '_'):] ,v) for (k, v) in POST.items() if k.startswith(tech.lower() + '_'))

