from reo.src.dat_file_manager import big_number


class IncentiveProvider(object):

    def __init__(self, name, incentives_dict):
        """

        :param name: str, either 'federal', 'state', or 'utility'
        :param incentives_dict: dict of POST params, filtered by 'pv' or 'batt'

        NOTE: future POST structure will not require filtering by 'pv' or 'batt'
        """
        self.itc = incentives_dict.get('itc_' + name)
        self.itc_max = incentives_dict.get('itc_' + name + '_max') or big_number
        self.rebate = incentives_dict.get('rebate_' + name)   # $/kW
        self.rebate_max = incentives_dict.get('rebate_' + name + '_max') or big_number


class ProductionBasedIncentive(object):

    def __init__(self, pbi=None, pbi_max=big_number, pbi_years=big_number, pbi_system_max=big_number):

        self.us_dollars_per_kw = pbi
        self.max_us_dollars_per_kw = pbi_max
        self.duration_years = pbi_years
        self.max_kw = pbi_system_max


class Incentives(object):
    """
    high level incentives object for attaching to production technologies and storage
    """

    def __init__(self, POST, tech=None, include_production_based=False):

        if tech:  # not needed once we modify POST dict
            filtered_kwargs = self._filter_inputs(tech, POST)
        else:
            filtered_kwargs = POST

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
        import pdb; pdb.set_trace()
        return dict((k[len(tech.lower() + '_'):] ,v) for (k, v) in POST.items() if k.startswith(tech.lower() + '_'))

