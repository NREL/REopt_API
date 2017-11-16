

class Financial(object):
    """
    All user-input discount and growth rates are assumed in real terms
    """

    def __init__(self,
                 om_cost_growth_pct,
                 escalation_pct,
                 offtaker_tax_pct,
                 offtaker_discount_pct,
                 analysis_years,
                 owner_tax_pct=None,
                 owner_discount_pct=None,
                 **kwargs
                 ):
        self.om_cost_growth_pct = om_cost_growth_pct
        self.escalation_pct = escalation_pct
        self.owner_tax_pct = owner_tax_pct
        self.offtaker_tax_pct = offtaker_tax_pct
        self.owner_discount_pct = owner_discount_pct
        self.offtaker_discount_pct = offtaker_discount_pct
        self.analysis_years = analysis_years

        # set-up direct ownership
        if self.owner_discount_pct is None:
            self.owner_discount_pct = self.offtaker_discount_pct
        if self.owner_tax_pct is None:
            self.owner_tax_pct = self.offtaker_tax_pct


class Site(object):

    def __init__(self, dfm, land_acres=None, roof_squarefeet=None, **kwargs):

        self.land_acres = land_acres
        self.roof_squarefeet = roof_squarefeet
        self.financial = Financial(**kwargs['Financial'])
        dfm.add_site(self)
