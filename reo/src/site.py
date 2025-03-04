# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.


class Financial(object):
    """
    All user-input discount and growth rates are assumed in real terms
    """

    def __init__(self,
                 om_cost_escalation_pct,
                 escalation_pct,
                 generator_fuel_escalation_pct,
                 boiler_fuel_escalation_pct,
                 chp_fuel_escalation_pct,
                 newboiler_fuel_escalation_pct,
                 offtaker_tax_pct,
                 offtaker_discount_pct,
                 analysis_years,
                 third_party_ownership,
                 owner_tax_pct,
                 owner_discount_pct,
                 co2_cost_us_dollars_per_tonne,
                 nox_cost_us_dollars_per_tonne_grid,
                 so2_cost_us_dollars_per_tonne_grid,
                 pm25_cost_us_dollars_per_tonne_grid,
                 nox_cost_us_dollars_per_tonne_onsite_fuelburn,
                 so2_cost_us_dollars_per_tonne_onsite_fuelburn,
                 pm25_cost_us_dollars_per_tonne_onsite_fuelburn,
                 co2_cost_escalation_pct,
                 nox_cost_escalation_pct,
                 so2_cost_escalation_pct,
                 pm25_cost_escalation_pct,
                 **kwargs
                 ):
        self.om_cost_escalation_pct = om_cost_escalation_pct
        self.escalation_pct = escalation_pct
        self.generator_fuel_escalation_pct = generator_fuel_escalation_pct
        self.boiler_fuel_escalation_pct = boiler_fuel_escalation_pct
        self.chp_fuel_escalation_pct = chp_fuel_escalation_pct
        self.newboiler_fuel_escalation_pct = newboiler_fuel_escalation_pct
        self.owner_tax_pct = owner_tax_pct
        self.offtaker_tax_pct = offtaker_tax_pct
        self.owner_discount_pct = owner_discount_pct
        self.third_party_ownership = third_party_ownership
        self.offtaker_discount_pct = offtaker_discount_pct
        self.analysis_years = analysis_years
        self.other_capital_costs_us_dollars = kwargs.get('other_capital_costs_us_dollars')
        self.other_annual_costs_us_dollars_per_year = kwargs.get('other_annual_costs_us_dollars_per_year')
        self.co2_cost_us_dollars_per_tonne = co2_cost_us_dollars_per_tonne
        self.nox_cost_us_dollars_per_tonne_grid = nox_cost_us_dollars_per_tonne_grid
        self.so2_cost_us_dollars_per_tonne_grid = so2_cost_us_dollars_per_tonne_grid
        self.pm25_cost_us_dollars_per_tonne_grid = pm25_cost_us_dollars_per_tonne_grid
        self.nox_cost_us_dollars_per_tonne_onsite_fuelburn = nox_cost_us_dollars_per_tonne_onsite_fuelburn
        self.so2_cost_us_dollars_per_tonne_onsite_fuelburn = so2_cost_us_dollars_per_tonne_onsite_fuelburn
        self.pm25_cost_us_dollars_per_tonne_onsite_fuelburn = pm25_cost_us_dollars_per_tonne_onsite_fuelburn
        self.co2_cost_escalation_pct = co2_cost_escalation_pct
        self.nox_cost_escalation_pct = nox_cost_escalation_pct
        self.so2_cost_escalation_pct = so2_cost_escalation_pct
        self.pm25_cost_escalation_pct = pm25_cost_escalation_pct

        # set-up direct ownership
        if self.third_party_ownership is False:
            self.owner_discount_pct = self.offtaker_discount_pct
            self.owner_tax_pct = self.offtaker_tax_pct


class Site(object):

    def __init__(self, dfm, land_acres=None, roof_squarefeet=None,
    renewable_electricity_min_pct=None, renewable_electricity_max_pct=None,
    co2_emissions_reduction_min_pct=None, co2_emissions_reduction_max_pct=None,
    include_exported_elec_emissions_in_total=None,include_exported_renewable_electricity_in_total=None,
     **kwargs):

        self.land_acres = land_acres
        self.roof_squarefeet = roof_squarefeet
        self.financial = Financial(**kwargs['Financial'])
        self.renewable_electricity_min_pct = renewable_electricity_min_pct
        self.renewable_electricity_max_pct = renewable_electricity_max_pct
        self.co2_emissions_reduction_min_pct = co2_emissions_reduction_min_pct
        self.co2_emissions_reduction_max_pct = co2_emissions_reduction_max_pct
        self.include_exported_elec_emissions_in_total = include_exported_elec_emissions_in_total
        self.include_exported_renewable_electricity_in_total = include_exported_renewable_electricity_in_total
        dfm.add_site(self)
