

class Financial(object):
    """
    All user-input discount and growth rates are assumed in real terms
    """

    def __init__(self,
                 om_cost_escalation_pct,
                 escalation_pct,
                 offtaker_tax_pct,
                 offtaker_discount_pct,
                 analysis_years,
                 two_party_ownership,
                 owner_tax_pct,
                 owner_discount_pct,
                 **kwargs
                 ):
        self.om_cost_escalation_pct = om_cost_escalation_pct
        self.escalation_pct = escalation_pct
        self.owner_tax_pct = owner_tax_pct
        self.offtaker_tax_pct = offtaker_tax_pct
        self.owner_discount_pct = owner_discount_pct
        self.two_party_ownership = two_party_ownership
        self.offtaker_discount_pct = offtaker_discount_pct
        self.analysis_years = analysis_years

        # set-up direct ownership
        if self.two_party_ownership is False:
            self.owner_discount_pct = self.offtaker_discount_pct
            self.owner_tax_pct = self.offtaker_tax_pct


class Site(object):

    def __init__(self, dfm, land_acres=None, roof_squarefeet=None, **kwargs):

        self.land_acres = land_acres
        self.roof_squarefeet = roof_squarefeet
        self.financial = Financial(**kwargs['Financial'])
        dfm.add_site(self)
