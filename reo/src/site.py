# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************


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

    def __init__(self, dfm, land_acres=None, roof_squarefeet=None,
            renewable_generation_min_pct=None,
            renewable_generation_max_pct=None,
            emissions_reduction_min_pct=None,
            emissions_reduction_max_pct=None,
            emissions_reduction_accounting_method=None,
            renewable_generation_accounting_method=None,
            **kwargs):

        self.renewable_generation_min_pct = renewable_generation_min_pct
        self.renewable_generation_max_pct = renewable_generation_max_pct
        self.emissions_reduction_min_pct = emissions_reduction_min_pct
        self.emissions_reduction_max_pct = emissions_reduction_max_pct
        self.emissions_reduction_accounting_method = emissions_reduction_accounting_method
        self.renewable_generation_accounting_method = renewable_generation_accounting_method

        self.land_acres = land_acres
        self.roof_squarefeet = roof_squarefeet
        self.financial = Financial(**kwargs['Financial'])
        dfm.add_site(self)
