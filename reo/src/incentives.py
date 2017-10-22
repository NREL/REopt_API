from reo.src.dat_file_manager import big_number


class IncentiveProvider(object):

    def __init__(self, name, incentives_dict):
        """

        :param name: str, either 'federal', 'state', or 'utility'
        :param incentives_dict: dict of POST params, filtered by 'pv' or 'batt'
        """

        # ITC only applies to federal, since don't track other tax rates
        if name == 'federal':
            self.itc = incentives_dict.get(name + 'itc_pct')
            self.itc_max = big_number

            # if 0 max passed in with an incentive, treat incentive as 0
            if self.itc_max == 0:
                self.itc = 0

        else: # region == 'state' or region == 'utility'
            self.ibi = incentives_dict.get(name + 'ibi_pct')
            self.ibi_max = incentives_dict.get(name + '_ibi_max_us_dollars', big_number)

            if self.ibi_max == 0:
                self.ibi = 0

        self.rebate = incentives_dict.get(name + '_rebate_us_dollars_per_kw')   # $/kW
        self.rebate_max = incentives_dict.get(name + '_rebate_max_us_dollars', big_number)

        if self.rebate_max == 0:
            self.rebate = 0


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

    def __init__(self, POST, macrs_years=5, macrs_bonus_fraction=0.5, macrs_itc_reduction=0.5,
                 include_production_based=False):

        filtered_kwargs = POST

        self.federal = IncentiveProvider('federal', incentives_dict=filtered_kwargs)
        self.state = IncentiveProvider('state', incentives_dict=filtered_kwargs)
        self.utility = IncentiveProvider('utility', incentives_dict=filtered_kwargs)

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

        # Modify MACRs reduction if no itc
        if self.federal.itc == 0 and self.total.itc == 0:
            self.macrs_itc_reduction = 0

        if include_production_based:
            self.production_based = ProductionBasedIncentive(**filtered_kwargs)
        else:
            self.production_based = None
