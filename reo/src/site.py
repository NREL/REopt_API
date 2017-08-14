

class Financials(object):
    """
    All user-input discount and growth rates are assumed in real terms
    """

    def __init__(self,
                 rate_inflation=0.01,
                 rate_escalation=0.02,
                 owner_tax_rate=None,
                 offtaker_tax_rate=0.35,
                 owner_discount_rate=None,
                 offtaker_discount_rate=0.08,
                 analysis_period=25,
                 **kwargs
                 ):
        self.rate_inflation = rate_inflation
        self.rate_escalation = rate_escalation
        self.owner_tax_rate = owner_tax_rate
        self.offtaker_tax_rate = offtaker_tax_rate
        self.owner_discount_rate = owner_discount_rate
        self.offtaker_discount_rate = offtaker_discount_rate
        self.analysis_period = analysis_period

        # set-up direct ownership
        if self.owner_discount_rate is None:
            self.owner_discount_rate = self.offtaker_discount_rate
        if self.owner_tax_rate is None:
            self.owner_tax_rate = self.offtaker_tax_rate

        self.offtaker_discount_rate_nominal = (1 + self.offtaker_discount_rate) * (1 + self.rate_inflation) - 1
        self.owner_discount_rate_nominal = (1 + self.owner_discount_rate) * (1 + self.rate_inflation) - 1
        self.rate_escalation_nominal = (1 + self.rate_escalation) * (1 + self.rate_inflation) - 1


class Site(object):

    def __init__(self, land_area=None, roof_area=None, **kwargs):

        self.land_acres = land_area
        self.roof_squarefeet = roof_area
        self.financials = Financials(**kwargs)
