# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
from reo.src.data_manager import big_number
from reo.nested_inputs import macrs_five_year, macrs_seven_year


class IncentiveProvider(object):

    def __init__(self, name, **kwargs):
        """

        :param name: str, either 'federal', 'state', or 'utility'
        :param kwargs: dict of POST params
        """

        # ITC only applies to federal, since don't track other tax rates
        if name == 'federal':
            self.itc = kwargs.get(name + '_itc_pct')
            self.itc_max = big_number

            # if 0 max passed in with an incentive, treat incentive as 0
            if self.itc_max == 0:
                self.itc = 0

        else: # region == 'state' or region == 'utility'
            self.ibi = kwargs.get(name + '_ibi_pct')
            self.ibi_max = kwargs.get(name + '_ibi_max_us_dollars', big_number)

            if self.ibi_max == 0:
                self.ibi = 0

        self.rebate = kwargs.get(name + '_rebate_us_dollars_per_kw')   # $/kW
        self.rebate_max = kwargs.get(name + '_rebate_max_us_dollars', big_number)

        if self.rebate_max == 0:
            self.rebate = 0


class ProductionBasedIncentive(object):

    def __init__(self, pbi_us_dollars_per_kwh, pbi_max_us_dollars, pbi_years, pbi_system_max_kw, **kwargs):

        self.us_dollars_per_kw = pbi_us_dollars_per_kwh
        self.max_us_dollars_per_year = pbi_max_us_dollars
        self.years = pbi_years
        self.max_kw = pbi_system_max_kw


class Incentives(object):
    """
    high level incentives object for attaching to production technologies and storage
    """

    def __init__(self, macrs_option_years, macrs_bonus_pct, macrs_itc_reduction, **kwargs):

        self.federal = IncentiveProvider('federal', **kwargs)
        self.state = IncentiveProvider('state', **kwargs)
        self.utility = IncentiveProvider('utility', **kwargs)

        self.macrs_bonus_pct = macrs_bonus_pct
        self.macrs_itc_reduction = macrs_itc_reduction

        if macrs_option_years == 5:
            self.macrs_schedule = macrs_five_year
        elif macrs_option_years == 7:
            self.macrs_schedule = macrs_seven_year
        elif macrs_option_years == 0:
            self.macrs_bonus_pct = 0
            self.macrs_itc_reduction = 0
            self.macrs_schedule = [0]
        else:
            raise ValueError("macrs_option_years must be 0, 5 or 7.")

        # Modify MACRs reduction if no itc
        if self.federal.itc == 0:
            self.macrs_itc_reduction = 0

        self.production_based = ProductionBasedIncentive(**kwargs)

class IncentivesNoProdBased(object):
    """
    high level incentives object for attaching to production technologies and storage
    """

    def __init__(self, macrs_option_years, macrs_bonus_pct, macrs_itc_reduction, **kwargs):

        self.federal = IncentiveProvider('federal', **kwargs)
        self.state = IncentiveProvider('state', **kwargs)
        self.utility = IncentiveProvider('utility', **kwargs)

        self.macrs_bonus_pct = macrs_bonus_pct
        self.macrs_itc_reduction = macrs_itc_reduction

        if macrs_option_years == 5:
            self.macrs_schedule = macrs_five_year
        elif macrs_option_years == 7:
            self.macrs_schedule = macrs_seven_year
        elif macrs_option_years == 0:
            self.macrs_bonus_pct = 0
            self.macrs_itc_reduction = 0
            self.macrs_schedule = [0]
        else:
            raise ValueError("macrs_option_years must be 0, 5 or 7.")

        # Modify MACRs reduction if no itc
        if self.federal.itc == 0:
            self.macrs_itc_reduction = 0