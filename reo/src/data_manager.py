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
import copy
from reo.src.urdb_parse import UrdbParse
from reo.utilities import annuity, degradation_factor, slope, intercept, insert_p_after_u_bp, insert_p_bp, \
    insert_u_after_p_bp, insert_u_bp, setup_capital_cost_incentive, annuity_escalation
max_incentive = 1.0e10

big_number = 1.0e10
squarefeet_to_acre = 2.2957e-5


def get_techs_not_none(techs, cls):
    ret = []
    for tech in techs:
        if eval('cls.' + tech) is not None:
            ret.append(tech)
    return ret


class DataManager:
    """
    Creates input dicts for reopt.jl and manages data transfer between Celery tasks
    """

    def __init__(self, run_id, n_timesteps=8760):
        self.pvs = []
        self.pvnms = []
        self.pv1 = None
        self.pv1nm = None
        self.wind = None
        self.windnm = None
        self.generator = None
        self.chp = None
        self.util = None
        self.boiler = None
        self.elecchl = None
        self.absorpchl = None
        self.storage = None
        self.hot_tes = None
        self.cold_tes = None
        self.site = None
        self.elec_tariff = None
        self.fuel_tariff = None
        self.load = None
        self.reopt_inputs = None
        self.reopt_inputs_bau = None

        # following attributes used to pass data to process_results.py
        self.LoadProfile = {}
        self.year_one_energy_cost_series_us_dollars_per_kwh = []
        self.year_one_demand_cost_series_us_dollars_per_kw = []

        self.available_techs = ['pv1', 'pv1nm', 'wind', 'windnm', 'generator', 'chp', 'boiler',
                                'elecchl', 'absorpchl']  # order is critical for REopt! Note these are passed to reopt.jl as uppercase
        self.available_tech_classes = ['PV1', 'WIND', 'GENERATOR', 'CHP', 'BOILER',
                                       'ELECCHL', 'ABSORPCHL']  # this is a REopt 'class', not a python class
        self.available_loads = ['retail', 'wholesale', 'export', 'storage', 'boiler', 'tes']  # order is critical for REopt!
        self.bau_techs = []
        self.NMILRegime = ['BelowNM', 'NMtoIL', 'AboveIL']
        self.fuel_burning_techs = ['GENERATOR', 'CHP']

        self.run_id = run_id
        self.n_timesteps = n_timesteps
        self.pwf_e = 0  # used in results.py -> outage_costs.py to escalate & discount avoided outage costs

    def add_load(self, load):
        self.LoadProfile["year_one_electric_load_series_kw"] = load.load_list
        self.LoadProfile["critical_load_series_kw"] = load.critical_load_series_kw
        self.LoadProfile["resilience_check_flag"] = load.resilience_check_flag
        self.LoadProfile["sustain_hours"] = load.sustain_hours
        self.LoadProfile["annual_kwh"] = load.annual_kwh
        self.load = load
        
    def add_load_boiler_fuel(self, load):
        self.LoadProfile["year_one_heating_load_series_mmbtu"] = load.load_list
        self.LoadProfile["annual_heating_mmbtu"] = load.annual_mmbtu
        self.heating_load = load
        
    def add_load_chiller_electric(self, load):
        self.LoadProfile["year_one_cooling_load_series_mmbtu"] = load.load_list
        self.LoadProfile["annual_cooling_kwh"] = load.annual_mmbtu
        self.cooling_load = load
        
    def add_boiler(self, boiler):
        self.boiler = boiler
        self.bau_techs.append('boiler')

    def add_electric_chiller(self, electric_chiller):
        self.elecchl = electric_chiller
        self.bau_techs.append('elecchl')

    def add_pv(self, pv):
        junk = pv.prod_factor  # avoids redundant PVWatts call for pvnm
        self.pvs.append(pv)
        self.pvnms.append(copy.deepcopy(pv))
        self.pvnms[-1].nmil_regime = 'NMtoIL'

        pv_number = len(self.pvs)

        if pv.existing_kw > 0:
            self.bau_techs = ["pv"+str(pv_number), "pv"+str(pv_number)+"nm"] + self.bau_techs

        # update self.available_techs (baseline is ['pv1', 'pv1nm', 'wind', 'windnm', 'generator'])
        if pv_number > 1:
            i = pv_number - 1
            self.available_techs = self.available_techs[:i*2] + ["pv"+str(pv_number), "pv"+str(pv_number)+"nm"] + \
                                   self.available_techs[i*2:]
            self.available_tech_classes = self.available_tech_classes[:i] + ["PV" + str(pv_number)] + \
                                   self.available_tech_classes[i:]
            # eg. ['pv1', 'pvnm1', 'pv2', 'pvnm2', 'wind', 'windnm', 'generator']

        # for backwards compatibility with all self._get* methods we need to attach the individual PV objects to self:
        exec("self.pv" + str(pv_number) + " = self.pvs[{}]".format(pv_number-1))
        exec("self.pv" + str(pv_number) + "nm" + " = self.pvnms[{}]".format(pv_number - 1))

    def add_wind(self, wind):

        junk = wind.prod_factor  # avoids redundant WindToolkit call for windnm
        self.wind = wind
        self.windnm = copy.deepcopy(wind)
        self.windnm.nmil_regime = 'NMtoIL'

    def add_util(self, util):
        self.util = util

    def add_generator(self, generator):
        self.generator = generator

        if self.generator.existing_kw > 0:

            # following if-clause is to avoid appending generator twice in the bau_techs list
            # for the test-case when two tests are run under same class definition (e.g. test_diesel_generator.py)
            # bau_techs will never have more than 1 entry for 'generator'
            if 'generator' not in self.bau_techs:
                self.bau_techs.append('generator')

    def add_chp(self, chp):
        self.chp = chp

    def add_absorption_chiller(self, absorption_chiller):
        self.absorpchl = absorption_chiller

    def add_site(self, site):
        self.site = site

    def add_storage(self, storage):
        self.storage = storage
        # storage_bau.dat gets same definitions as storage.dat so that initializations don't fail in bau case
        # however, storage is typically 'turned off' by having max size set to zero in maxsizes_bau.dat
        # TODO: save reopt_inputs dictionary?
        # efficiencies are defined in finalize method because their arrays depend on which Techs are defined

    def add_hot_tes(self, hot_tes):
        self.hot_tes = hot_tes

        # All attributes are written in finalize method because they are stacked 1..2 for hot_tes..cold_tes storages

    def add_cold_tes(self, cold_tes):
        self.cold_tes = cold_tes

        # All attributes are written in finalize method because they are stacked 1..2 for hot_tes..cold_tes storages

    def add_elec_tariff(self, elec_tariff):
        self.elec_tariff = elec_tariff

    def add_fuel_tariff(self, fuel_tariff):
        self.fuel_tariff = fuel_tariff

    def _get_REopt_pwfs(self, techs):
        sf = self.site.financial
        pwf_owner = annuity(sf.analysis_years, 0, sf.owner_discount_pct) # not used in REopt
        pwf_offtaker = annuity(sf.analysis_years, 0, sf.offtaker_discount_pct)  # not used in REopt
        pwf_om = annuity(sf.analysis_years, sf.om_cost_escalation_pct, sf.owner_discount_pct)
        pwf_e = annuity(sf.analysis_years, sf.escalation_pct, sf.offtaker_discount_pct)
        pwf_boiler_fuel = annuity(sf.analysis_years, sf.boiler_fuel_escalation_pct, sf.offtaker_discount_pct)
        pwf_chp_fuel = annuity(sf.analysis_years, sf.chp_fuel_escalation_pct, sf.offtaker_discount_pct)
        self.pwf_e = pwf_e
        # pwf_op = annuity(sf.analysis_years, sf.escalation_pct, sf.owner_discount_pct)

        if sf.two_party_ownership:
            two_party_factor = (pwf_offtaker * (1 - sf.offtaker_tax_pct)) \
                                / (pwf_owner * (1 - sf.owner_tax_pct))
        else:
            two_party_factor = 1

        levelization_factor = list()
        pwf_fuel_by_tech = list()

        for tech in techs:

            if eval('self.' + tech) is not None:

                if tech.startswith("pv"):  # pv has degradation

                    #################
                    # NOTE: I don't think that levelization factors should include an escalation rate.  The degradation
                    # does not escalate in out years.
                    ################
                    degradation_pct = eval('self.' + tech + '.degradation_pct')
                    levelization_factor.append(round(degradation_factor(sf.analysis_years, degradation_pct), 5))
                else:
                    levelization_factor.append(1.0)

                # Assign pwf_fuel_by_tech
                if tech in ['chp', 'chpnm']:
                    pwf_fuel_by_tech.append(round(pwf_chp_fuel, 5))
                elif tech == 'boiler':
                    pwf_fuel_by_tech.append(round(pwf_boiler_fuel, 5))
                else:
                    pwf_fuel_by_tech.append(round(pwf_e, 5))

        return levelization_factor, pwf_e, pwf_om, two_party_factor, pwf_boiler_fuel, pwf_chp_fuel, pwf_fuel_by_tech

    def _get_REopt_production_incentives(self, techs):
        sf = self.site.financial
        pwf_prod_incent = list()
        prod_incent_rate = list()
        max_prod_incent = list()
        max_size_for_prod_incent = list()

        production_incentive_rate = list()

        for tech in techs:

            if eval('self.' + tech) is not None:
                
                if tech not in ['util', 'generator', 'boiler', 'elecchl', 'absorpchl']:

                    # prod incentives don't need escalation
                    if tech.startswith("pv"):  # PV has degradation
                        pwf_prod_incent.append(
                            annuity_escalation(eval('self.' + tech + '.incentives.production_based.years'),
                                               -1 * eval('self.' + tech + '.degradation_pct'),
                                               sf.owner_discount_pct))
                    else:
                        pwf_prod_incent.append(
                            annuity(eval('self.' + tech + '.incentives.production_based.years'),
                                    0, sf.owner_discount_pct))
                    max_prod_incent.append(
                        eval('self.' + tech + '.incentives.production_based.max_us_dollars_per_year')
                    )
                    max_size_for_prod_incent.append(
                        eval('self.' + tech + '.incentives.production_based.max_kw')
                    )
                    for load in self.available_loads:
                        prod_incent_rate.append(
                            eval('self.' + tech + '.incentives.production_based.us_dollars_per_kw')
                        )

                    production_incentive_rate.append(
                        eval('self.' + tech + '.incentives.production_based.us_dollars_per_kw')
                    )
                else:

                    pwf_prod_incent.append(0.0)
                    max_prod_incent.append(0.0)
                    max_size_for_prod_incent.append(0.0)
                    production_incentive_rate.append(0.0)

                    for load in self.available_loads:
                        prod_incent_rate.append(0.0)

        return pwf_prod_incent, prod_incent_rate, max_prod_incent, max_size_for_prod_incent, production_incentive_rate

    def _get_REopt_cost_curve(self, techs):
        regions = ['utility', 'state', 'federal', 'combined']
        cap_cost_slope = list()
        cap_cost_x = list()
        cap_cost_yint = list()
        n_segments_max = 0  # tracking the maximum number of cost curve segments
        n_segments = 1
        n_segments_list = list()
        tech_to_size = float(big_number)

        for tech in techs:

            if eval('self.' + tech) is not None and tech not in ['util', 'boiler', 'elecchl']:

                existing_kw = 0.0
                if hasattr(eval('self.' + tech), 'existing_kw'):
                    if eval('self.' + tech + '.existing_kw') is not None:
                        existing_kw = eval('self.' + tech + '.existing_kw')

                tech_cost = eval('self.' + tech + '.installed_cost_us_dollars_per_kw')
                tech_incentives = dict()

                for region in regions[:-1]:
                    tech_incentives[region] = dict()

                    if tech not in ['generator']:

                        if region == 'federal' or region == 'total':
                            tech_incentives[region]['%'] = eval('self.' + tech + '.incentives.' + region + '.itc')
                            tech_incentives[region]['%_max'] = eval('self.' + tech + '.incentives.' + region + '.itc_max')
                        else:  # region == 'state' or region == 'utility'
                            tech_incentives[region]['%'] = eval('self.' + tech + '.incentives.' + region + '.ibi')
                            tech_incentives[region]['%_max'] = eval('self.' + tech + '.incentives.' + region + '.ibi_max')

                        tech_incentives[region]['rebate'] = eval('self.' + tech + '.incentives.' + region + '.rebate')
                        tech_incentives[region]['rebate_max'] = eval('self.' + tech + '.incentives.' + region + '.rebate_max')

                        # Workaround to consider fact that REopt incentive calculation works best if "unlimited" incentives are entered as 0
                        if tech_incentives[region]['%_max'] == max_incentive:
                            tech_incentives[region]['%_max'] = 0.0
                        if tech_incentives[region]['rebate_max'] == max_incentive:
                            tech_incentives[region]['rebate_max'] = 0.0

                    else:  # for generator there are no incentives
                        tech_incentives[region]['%'] = 0.0
                        tech_incentives[region]['%_max'] = 0.0
                        tech_incentives[region]['rebate'] = 0.0
                        tech_incentives[region]['rebate_max'] = 0.0

                        # Intermediate Cost curve
                xp_array_incent = dict()
                xp_array_incent['utility'] = [0.0, tech_to_size]  #kW
                yp_array_incent = dict()
                yp_array_incent['utility'] = [0.0, tech_to_size * tech_cost]  #$

                # Final cost curve
                cost_curve_bp_x = [0.0]
                cost_curve_bp_y = [0.0]

                for r in range(len(regions)-1):

                    region = regions[r]  # regions = ['utility', 'state', 'federal', 'combined']
                    next_region = regions[r + 1]

                    # Apply incentives, initialize first value
                    xp_array_incent[next_region] = [0.0]
                    yp_array_incent[next_region] = [0.0]

                    # percentage based incentives
                    p = float(tech_incentives[region]['%'])
                    p_cap = float(tech_incentives[region]['%_max'])

                    # rebates, for some reason called 'u' in REopt
                    u = float(tech_incentives[region]['rebate'])
                    u_cap = float(tech_incentives[region]['rebate_max'])

                    # reset switches and break point counter
                    switch_percentage = False
                    switch_rebate = False

                    if p == 0 or p_cap == 0:
                        switch_percentage = True
                    if u == 0 or u_cap == 0:
                        switch_rebate = True

                    # start at second point, first is always zero
                    for point in range(1, len(xp_array_incent[region])):

                        # previous points
                        xp_prev = xp_array_incent[region][point - 1]
                        yp_prev = yp_array_incent[region][point - 1]

                        # current, unadjusted points
                        xp = xp_array_incent[region][point]
                        yp = yp_array_incent[region][point]

                        # initialize the adjusted points on cost curve
                        xa = xp
                        ya = yp

                        # initialize break points
                        u_xbp = 0.0
                        u_ybp = 0.0
                        p_xbp = 0.0
                        p_ybp = 0.0

                        if not switch_rebate:
                            u_xbp = u_cap / u
                            u_ybp = slope(xp_prev, yp_prev, xp, yp) * u_xbp + intercept(xp_prev, yp_prev, xp, yp)

                        if not switch_percentage:
                            p_xbp = (p_cap / p - intercept(xp_prev, yp_prev, xp, yp)) / slope(xp_prev, yp_prev, xp, yp)
                            p_ybp = p_cap / p

                        if ((p * yp) < p_cap or p_cap == 0) and ((u * xp) < u_cap or u_cap == 0):
                            ya = yp - (p * yp + u * xp)
                        elif (p * yp) < p_cap and (u * xp) >= u_cap:
                            if not switch_rebate:
                                if u * xp != u_cap:
                                    xp_array_incent, yp_array_incent = \
                                        insert_u_bp(xp_array_incent, yp_array_incent, next_region, u_xbp, u_ybp, p, u_cap)
                                switch_rebate = True
                            ya = yp - (p * yp + u_cap)
                        elif (p * yp) >= p_cap and (u * xp) < u_cap:
                            if not switch_percentage:
                                if p * yp != p_cap:
                                    xp_array_incent, yp_array_incent = \
                                        insert_p_bp(xp_array_incent, yp_array_incent, next_region, p_xbp, p_ybp, u, p_cap)
                                switch_percentage = True
                            ya = yp - (p_cap + xp * u)
                        elif p * yp >= p_cap and u * xp >= u_cap:
                            if not switch_rebate and not switch_percentage:
                                if p_xbp == u_xbp:
                                    xp_array_incent, yp_array_incent = \
                                        insert_u_bp(xp_array_incent, yp_array_incent, next_region, u_xbp, u_ybp, p, u_cap)
                                    switch_percentage = True
                                    switch_rebate = True
                                elif p_xbp < u_xbp:
                                    if p * yp != p_cap:
                                        xp_array_incent, yp_array_incent = \
                                            insert_p_bp(xp_array_incent, yp_array_incent, next_region, p_xbp, p_ybp, u,
                                                        p_cap)
                                    switch_percentage = True
                                    if u * xp != u_cap:
                                        xp_array_incent, yp_array_incent = \
                                            insert_u_after_p_bp(xp_array_incent, yp_array_incent, next_region, u_xbp, u_ybp,
                                                                p, p_cap, u_cap)
                                    switch_rebate = True
                                else:
                                    if u * xp != u_cap:
                                        xp_array_incent, yp_array_incent = \
                                            insert_u_bp(xp_array_incent, yp_array_incent, next_region, u_xbp, u_ybp, p, u_cap)
                                    switch_rebate = True
                                    if p * yp != p_cap:
                                        xp_array_incent, yp_array_incent = \
                                            insert_p_after_u_bp(xp_array_incent, yp_array_incent, next_region, p_xbp, p_ybp,
                                                                u, u_cap, p_cap)
                                    switch_percentage = True
                            elif switch_rebate and not switch_percentage:
                                if p * yp != p_cap:
                                    xp_array_incent, yp_array_incent = \
                                        insert_p_after_u_bp(xp_array_incent, yp_array_incent, next_region, p_xbp, p_ybp, u,
                                                            u_cap, p_cap)
                                switch_percentage = True
                            elif switch_percentage and not switch_rebate:
                                if u * xp != u_cap:
                                    xp_array_incent, yp_array_incent = \
                                        insert_u_after_p_bp(xp_array_incent, yp_array_incent, next_region, u_xbp, u_ybp, p,
                                                            p_cap, u_cap)
                                switch_rebate = True

                            # Finally compute adjusted values
                            if p_cap == 0:
                                ya = yp - (p * yp + u_cap)
                            elif u_cap == 0:
                                ya = yp - (p_cap + u * xp)
                            else:
                                ya = yp - (p_cap + u_cap)

                        xp_array_incent[next_region].append(xa)
                        yp_array_incent[next_region].append(ya)

                        # compute cost curve, funky logic in REopt ignores everything except xa, ya
                        if region == 'federal':
                            cost_curve_bp_x.append(xa)
                            cost_curve_bp_y.append(ya)

                tmp_cap_cost_slope = list()
                tmp_cap_cost_yint = list()

                for seg in range(1, len(cost_curve_bp_x)):
                    tmp_slope = round((cost_curve_bp_y[seg] - cost_curve_bp_y[seg - 1]) /
                                      (cost_curve_bp_x[seg] - cost_curve_bp_x[seg - 1]), 0)
                    tmp_y_int = round(cost_curve_bp_y[seg] - tmp_slope * cost_curve_bp_x[seg], 0)

                    tmp_cap_cost_slope.append(tmp_slope)
                    tmp_cap_cost_yint.append(tmp_y_int)

                n_segments = len(tmp_cap_cost_slope)

                # Following logic modifies the cap cost segments to account for the tax benefits of the ITC and MACRs
                updated_cap_cost_slope = list()
                updated_y_intercept = list()

                for s in range(n_segments):

                    if cost_curve_bp_x[s + 1] > 0:
                        # Remove federal incentives for ITC basis and tax benefit calculations
                        itc = eval('self.' + tech + '.incentives.federal.itc')
                        rebate_federal = eval('self.' + tech + '.incentives.federal.rebate')
                        itc_unit_basis = (tmp_cap_cost_slope[s] + rebate_federal) / (1 - itc)

                    sf = self.site.financial
                    updated_slope = setup_capital_cost_incentive(
                        itc_basis=itc_unit_basis,  # input tech cost with incentives, but no ITC
                        replacement_cost=0,
                        replacement_year=sf.analysis_years,
                        discount_rate=sf.owner_discount_pct,
                        tax_rate=sf.owner_tax_pct,
                        itc=itc,
                        macrs_schedule=eval('self.' + tech + '.incentives.macrs_schedule'),
                        macrs_bonus_pct=eval('self.' + tech + '.incentives.macrs_bonus_pct'),
                        macrs_itc_reduction=eval('self.' + tech + '.incentives.macrs_itc_reduction')
                    )
                    # The way REopt incentives currently work, the federal rebate is the only incentive that doesn't reduce ITC basis
                    updated_slope -= rebate_federal
                    updated_cap_cost_slope.append(updated_slope)

                for p in range(1, n_segments + 1):
                    cost_curve_bp_y[p] = cost_curve_bp_y[p - 1] + updated_cap_cost_slope[p - 1] * \
                                                                  (cost_curve_bp_x[p] - cost_curve_bp_x[p - 1])
                    updated_y_intercept.append(cost_curve_bp_y[p] - updated_cap_cost_slope[p - 1] * cost_curve_bp_x[p])

                tmp_cap_cost_slope = updated_cap_cost_slope
                tmp_cap_cost_yint = updated_y_intercept

                """
                Adjust first cost curve segment to account for existing_kw.
                NOTE:
                - first X "breakpoint" and y-intercept must ALWAYS be zero (to be compatible with REopt constraints and
                    costing formulation.
                - if existing_kw > 0, then the first slope must also be zero (cannot be negative!).

                Steps:
                    1. find the segment for existing_kw
                    2. find the y-value for existing_kw (which is an x-value)
                    3. set the cost curve to x-axis from zero kw up to existing_kw
                    4. shift the rest of the cost curve down by the y-value found in step 2
                    5. reset n_segments (existing_kw can add a breakpoint, or take them away)
                """
                if existing_kw > 0:  # PV or Generator has existing_kw
                    # find the first index in cost_curve_bp_x that is larger than existing_kw, then reset cost curve
                    for i, bp in enumerate(cost_curve_bp_x[1:]):  # need to make sure existing_kw is never larger then last bp
                        if bp <= existing_kw:
                            continue
                        else:
                            y_shift = -(tmp_cap_cost_slope[i] * existing_kw + tmp_cap_cost_yint[i])
                            tmp_cap_cost_slope = [0.0] + tmp_cap_cost_slope[i:]
                            tmp_cap_cost_yint = [0.0] + [y + y_shift for y in tmp_cap_cost_yint[i:]]
                            cost_curve_bp_x = [0.0, existing_kw] + cost_curve_bp_x[i+1:]
                            n_segments = len(tmp_cap_cost_slope)
                            break

                # append the current Tech's segments to the arrays that will be passed to REopt
                cap_cost_slope += tmp_cap_cost_slope
                cap_cost_yint += tmp_cap_cost_yint
                cap_cost_x += cost_curve_bp_x

                # Have to take n_segments as the maximum number across all technologies
                n_segments_max = max(n_segments, n_segments_max)
                n_segments_list.append(n_segments)

            # [az] Not sure if we need this or not, first line is updated from DatFileManager and the rest may have been removed in this version
            elif eval('self.' + tech) is not None and tech in ['util', 'boiler', 'elecchl']:

                cap_cost_slope.append(0.0)
                cap_cost_yint.append(0.0)
                cap_cost_x += [0.0, big_number]

                # Have to take n_segments as the maximum number across all technologies
                n_segments_max = max(n_segments, n_segments_max)
                n_segments_list.append(n_segments)

        """
        Last step in creating cost curve is filling in the curves for each tech that does not have
        n_segments == n_segments_max. The filling in is achieved by duplicating the origin with zero cap_cost_slope for
        as many additional segments that are needed.
        """
        adj_cap_cost_slope, adj_cap_cost_x, adj_cap_cost_yint = list(), list(), list()
        for n_segments in n_segments_list:
            slope_list = cap_cost_slope[0:n_segments]
            del cap_cost_slope[0:n_segments]
            y_list = cap_cost_yint[0:n_segments]
            del cap_cost_yint[0:n_segments]
            x_list = cap_cost_x[0:n_segments+1]
            del cap_cost_x[0:n_segments+1]

            n_segments_to_add = n_segments_max - n_segments
            adj_cap_cost_slope += [0.0]*n_segments_to_add + slope_list
            adj_cap_cost_yint += [0.0]*n_segments_to_add + y_list
            adj_cap_cost_x += [0.0]*n_segments_to_add + x_list

        return adj_cap_cost_slope, adj_cap_cost_x, adj_cap_cost_yint, n_segments_max

    def _get_REopt_techToNMILMapping(self, techs):
        TechToNMILMapping = list()
        
        if len(techs) == 0:
            TechsByNMILRegime = []
            NMIL_regime = []
        else:
            TechsByNMILRegime = [[] for _ in self.NMILRegime]
            NMIL_regime = self.NMILRegime
            
        for tech in techs:

            if eval('self.' + tech) is not None:

                tech_regime = eval('self.' + tech + '.nmil_regime')

                for i,regime in enumerate(self.NMILRegime):
                    if regime == tech_regime:
                        TechToNMILMapping.append(1)
                        TechsByNMILRegime[i].append(tech.upper())
                    else:
                        TechToNMILMapping.append(0)

#        for regime in self.NMILRegime:
#            tech_nmil_reg = list()
#            for tech in techs:
#                if eval('self.' + tech) is not None:
#                    tech_regime = eval('self.' + tech + '.nmil_regime')
#                    if regime == tech_regime:
#                        TechsByNMILRegime.append(tech)
#
#            TechsByNMILRegime.append(tech_nmil_reg)

        return TechToNMILMapping, TechsByNMILRegime, NMIL_regime

    def _get_REopt_array_tech_load(self, techs):
        """
        Many arrays are built from Tech and Load. As many as possible are defined here to reduce for-loop iterations
        :param techs: list of strings, eg. ['pv', 'pvnm']
        :return: tech_to_load, tech_to_location, derate, eta_storage_in, eta_storage_out, \
               om_cost_us_dollars_per_kw, om_cost_us_dollars_per_kwh, production_factor, charge_efficiency, \
               discharge_efficiency, techs_charging_storage, electric_derate
        """
        production_factor = list()
        chp_thermal_prod_factor = list()
        tech_to_load = list()
        tech_to_location = list()
        derate = list()
        electric_derate = list()
        eta_storage_in = list()
        eta_storage_out = list()
        eta_tes_in = list()
        eta_tes_out = list()
        om_cost_us_dollars_per_kw = list()
        om_cost_us_dollars_per_kwh = list()

        charge_efficiency = list()
        discharge_efficiency = list()

        for tech in techs:
            if eval('self.' + tech) is not None:
                derate.append(eval('self.' + tech + '.derate'))
                if tech.lower() != 'chp':
                    for pf in eval('self.' + tech + '.prod_factor'):
                        production_factor.append(float(pf))
                        electric_derate.append(1.0)
                else: 
                    pf_electric, pf_hot_thermal = self.chp.prod_factor
                    for pf in pf_electric:
                        production_factor.append(float(pf))
                        electric_derate.append(1.0)
                    for pf in pf_hot_thermal:
                        chp_thermal_prod_factor.append(float(pf))

                charge_efficiency.append(self.storage.rectifier_efficiency_pct *
                                                 self.storage.internal_efficiency_pct**0.5)
                charge_efficiency.append(self.hot_tes.internal_efficiency_pct)
                charge_efficiency.append(self.cold_tes.internal_efficiency_pct)        
                # Yearly fixed O&M per unit power
                if tech.lower() == 'boiler' or tech.lower() == 'elec_chl':
                    om_cost_us_dollars_per_kw.append(0)
                else:
                    om_cost_us_dollars_per_kw.append(eval('self.' + tech + '.om_cost_us_dollars_per_kw'))


                # only generator and chp techs have variable o&m cost
                if tech.lower() == 'generator':
                    om_cost_us_dollars_per_kwh.append(float(eval('self.' + tech + '.kwargs["om_cost_us_dollars_per_kwh"]')))
                elif tech.lower() == 'chp':
                    om_cost_us_dollars_per_kwh.append(eval('self.' + tech + '.om_cost_us_dollars_per_kwh'))
                else:
                    om_cost_us_dollars_per_kwh.append(0.0)

                for load in self.available_loads:

                    eta_storage_in.append(self.storage.rectifier_efficiency_pct *
                                          self.storage.internal_efficiency_pct**0.5 if load == 'storage' else float(1))

                    eta_tes_in.append(self.hot_tes.internal_efficiency_pct if load == 'tes' else 1)
                    eta_tes_in.append(self.cold_tes.internal_efficiency_pct if load == 'tes' else 1)

                    if eval('self.' + tech + '.can_serve(' + '"' + load + '"' + ')'):

                        tech_to_load.append(1)

                    else:

                        tech_to_load.append(0)

                    # By default, util can serve storage load.
                    # However, if storage is being modeled it can override grid-charging
                    if tech == 'util' and load == 'storage' and self.storage is not None:
                        tech_to_load[-1] = int(self.storage.canGridCharge)

                for location in ['roof', 'ground', 'both']:
                    if tech.startswith('pv'):
                        if eval('self.' + tech + '.location') == location:
                            tech_to_location.append(1)
                        else:
                            tech_to_location.append(0)
                    else:
                        tech_to_location.append(0)

        for load in self.available_loads:
            # eta_storage_out is array(Load) of real
            eta_storage_out.append(self.storage.inverter_efficiency_pct * self.storage.internal_efficiency_pct**0.5
                                   if load == 'storage' else 1.0)
            # Current TES efficiency input is just charging/in efficiency, so eta_tes_out is 1.
            eta_tes_out.append(1.0 if load == 'tes' else 1)
            eta_tes_out.append(1.0 if load == 'tes' else 1)
            
        # eta_storage_out is array(Load) of real
        discharge_efficiency.append(self.storage.inverter_efficiency_pct * self.storage.internal_efficiency_pct**0.5)
        # Current TES efficiency input is just charging/in efficiency, so eta_tes_out is 1.
        discharge_efficiency.append(1.0)
        discharge_efficiency.append(1.0)
                
        # In BAU case, storage.dat must be filled out for REopt initializations, but max size is set to zero
        #[az] TODO: rm tech_is_hot/cool/chp, rm prod_factor, update prodction_factor, update finalize
        return tech_to_load, tech_to_location, derate, eta_storage_in, eta_storage_out, \
               eta_tes_in, eta_tes_out, om_cost_us_dollars_per_kw, om_cost_us_dollars_per_kwh, production_factor, charge_efficiency, \
               discharge_efficiency, electric_derate

    def _get_REopt_techs(self, techs):
        reopt_techs = list()
        for tech in techs:

            if eval('self.' + tech) is not None:

                reopt_techs.append(tech.upper() if tech not in ['util'] else tech.upper() + '1')

        return reopt_techs

    def _get_REopt_tech_classes(self, techs, bau):
        """

        :param techs: list of strings, eg. ['pv1', 'pvnm1', 'util']
        :return: tech_classes, tech_class_min_size, tech_to_tech_class
        """
        if len(techs) == 0:
            return [0.0 for _ in self.available_tech_classes], [], [[] for _ in self.available_tech_classes]
        tech_class_min_size = list()  # array(TechClass)
        tech_to_tech_class = list()  # array(Tech, TechClass)
        techs_in_class = list()  # array(TechClass)
        for tc in self.available_tech_classes:
            min_sizes = [0.0]
            for tech in (x for x in techs if x.startswith(tc.lower()) and 'nm' not in x):
                if eval('self.' + tech) is not None:
                    if hasattr(eval('self.' + tech), 'existing_kw'):
                        if bau:
                            min_sizes.append((eval('self.' + tech + '.existing_kw') or 0.0))
                        else:
                            min_sizes.append((eval('self.' + tech + '.existing_kw') or 0.0) + (eval('self.' + tech + '.min_kw') or 0.0))
                    elif tech.lower() == 'boiler':
                        min_sizes.append(eval('self.' + tech + '.min_mmbtu_per_hr'))
                    else:
                        min_sizes.append((eval('self.' + tech + '.min_kw') or 0.0))

            tech_class_min_size.append(max(min_sizes))

        for tech in techs:

            if eval('self.' + tech) is not None:

                for tc in self.available_tech_classes:

                    if eval('self.' + tech + '.reopt_class').upper() == tc.upper():
                        tech_to_tech_class.append(1)
                    else:
                        tech_to_tech_class.append(0)

        for tc in self.available_tech_classes:
            class_list = list()
            for tech in techs:
                if eval('self.' + tech) is not None:
                    if eval('self.' + tech + '.reopt_class').upper() == tc.upper():
                        class_list.append(tech.upper() if tech is not 'util' else tech.upper() + '1')
            techs_in_class.append(class_list)

        return tech_class_min_size, tech_to_tech_class, techs_in_class


    def _get_REopt_tech_max_sizes_min_turn_down(self, techs, bau=False):
        max_sizes = list()
        min_turn_down = list()
        min_allowable_size = list()
        # default to large max size per location. Max size by roof, ground, both
        max_sizes_location = [1.0e9, 1.0e9, 1.0e9]
        pv_roof_limited, pv_ground_limited, pv_space_limited = False, False, False
        roof_existing_pv_kw = 0.0
        ground_existing_pv_kw = 0.0
        both_existing_pv_kw = 0.0
        for tech in techs:

            if eval('self.' + tech) is not None:
                existing_kw = 0.0
                if hasattr(eval('self.' + tech), 'existing_kw'):
                    if eval('self.' + tech + '.existing_kw') is not None:
                        existing_kw = eval('self.' + tech + '.existing_kw')

                if hasattr(eval('self.' + tech), 'min_turn_down_pct'):
                    min_turn_down.append(eval('self.' + tech + '.min_turn_down_pct'))
                else:
                    min_turn_down.append(0.0)

                if hasattr(eval('self.' + tech), 'min_allowable_kw'):
                    min_allowable_size.append(eval('self.' + tech + '.min_allowable_kw'))
                else:
                    min_allowable_size.append(0)

                beyond_existing_cap_kw = eval('self.' + tech + '.max_kw')  # default is big_number
                if tech.startswith('pv'):  # has acres_per_kw and kw_per_square_foot attributes, as well as location
                    if eval('self.' + tech + '.location') == 'both':
                        both_existing_pv_kw += existing_kw
                        if self.site.roof_squarefeet is not None and self.site.land_acres is not None:
                            # don't restrict unless they specify both land_area and roof_area,
                            # otherwise one of them is "unlimited" in UI
                            roof_max_kw = self.site.roof_squarefeet * eval('self.' + tech + '.kw_per_square_foot')
                            land_max_kw = self.site.land_acres / eval('self.' + tech + '.acres_per_kw')
                            beyond_existing_cap_kw = min(roof_max_kw + land_max_kw, beyond_existing_cap_kw)
                            pv_space_limited = True
                    elif eval('self.' + tech + '.location') == 'roof':
                        roof_existing_pv_kw += existing_kw
                        if self.site.roof_squarefeet is not None:
                            roof_max_kw = self.site.roof_squarefeet * eval('self.' + tech + '.kw_per_square_foot')
                            beyond_existing_cap_kw = min(roof_max_kw, beyond_existing_cap_kw)
                            pv_roof_limited = True

                    elif eval('self.' + tech + '.location') == 'ground':
                        ground_existing_pv_kw += existing_kw
                        if self.site.land_acres is not None:
                            land_max_kw = self.site.land_acres / eval('self.' + tech + '.acres_per_kw')
                            beyond_existing_cap_kw = min(land_max_kw, beyond_existing_cap_kw)
                            pv_ground_limited = True

                else:
                    if eval('self.' + tech + '.acres_per_kw') is not None:
                        if eval('self.' + tech + '.kw_per_square_foot') is not None:
                            if self.site.roof_squarefeet is not None and self.site.land_acres is not None:
                                # don't restrict unless they specify both land_area and roof_area,
                                # otherwise one of them is "unlimited" in UI
                                roof_max_kw = self.site.roof_squarefeet * eval('self.' + tech + '.kw_per_square_foot')
                                land_max_kw = self.site.land_acres / eval('self.' + tech + '.acres_per_kw')
                                beyond_existing_cap_kw = min(roof_max_kw + land_max_kw, beyond_existing_cap_kw)

                if tech.startswith('wind'):  # has acres_per_kw attribute
                    if self.site.land_acres is not None:
                        site_constraint_kw = self.site.land_acres / eval('self.' + tech + '.acres_per_kw')
                        if site_constraint_kw < 1500:
                            # turbines less than 1.5 MW aren't subject to the acres/kW limit
                            site_constraint_kw = 1500
                        beyond_existing_cap_kw = min(site_constraint_kw, beyond_existing_cap_kw)

                if bau and existing_kw > 0:  # existing PV in BAU scenario
                    max_sizes.append(float(existing_kw))
                elif tech.lower() == 'boiler':
                    max_sizes.append(eval('self.' + tech + '.max_mmbtu_per_hr'))
                else:
                    max_sizes.append(float(existing_kw + beyond_existing_cap_kw))

        if pv_roof_limited is True:
            max_sizes_location[0] = float(roof_existing_pv_kw/2 + roof_max_kw)
        if pv_ground_limited is True:
            max_sizes_location[1] = float(ground_existing_pv_kw/2 + land_max_kw)
        if pv_space_limited is True:
            max_sizes_location[2] = float(both_existing_pv_kw/2 + roof_max_kw + land_max_kw)
        # existing PV kW's divided by 2 b/c of the duplicate existing capacity created by `pv*nm`

        return max_sizes, min_turn_down, max_sizes_location, min_allowable_size

    def _get_time_steps_with_grid(self):
        """
        Obtains the subdivision of time steps with a grid connection and those
        without (i.e., under an outage).  Uses the utility's prod_factor value
        (1=connected, 0 o.w.) at each time step to obtain these sets, which
        are presented as lists.

        Parameters
            None
        Returns
            time_steps_with_grid -- list of ints indicating grid-connected
                time steps
            time_steps_without_grid -- list of ints indicating outage time
                steps
        """
        time_steps_with_grid = list()
        time_steps_without_grid = list()
        for i, pf in enumerate(self.util.prod_factor):
            if pf > 0.5:
                time_steps_with_grid.append(i+1)
            else:
                time_steps_without_grid.append(i+1)
        return time_steps_with_grid, time_steps_without_grid

    def finalize(self):
        """
        necessary for writing out parameters that depend on which Techs are defined
        eg. in REopt ProdFactor: array (Tech,Load,TimeStep).
        Note: whether or not a given Tech can serve a given Load can also be controlled via TechToLoadMatrix
        :return: None
        """
        reopt_techs = self._get_REopt_techs(self.available_techs)
        reopt_techs_bau = self._get_REopt_techs(self.bau_techs)

        tech_class_min_size, tech_to_tech_class, techs_in_class = self._get_REopt_tech_classes(self.available_techs, False)
        tech_class_min_size_bau, tech_to_tech_class_bau, techs_in_class_bau = self._get_REopt_tech_classes(self.bau_techs, True)

        tech_to_load, tech_to_location, derate, eta_storage_in, eta_storage_out, \
               eta_tes_in, eta_tes_out, om_cost_us_dollars_per_kw, om_cost_us_dollars_per_kwh, production_factor, charge_efficiency, \
               discharge_efficiency, electric_deratee = self._get_REopt_array_tech_load(self.available_techs)
        tech_to_load_bau, tech_to_location_bau, derate_bau, eta_storage_in_bau, eta_storage_out_bau, \
               eta_tes_in_bau, eta_tes_out_bau, om_cost_us_dollars_per_kw_bau, om_cost_us_dollars_per_kwh_bau, production_factor_bau, charge_efficiency_bau, \
               discharge_efficiency_bau, electric_derate_bau = self._get_REopt_array_tech_load(self.bau_techs)

        max_sizes, min_turn_down, max_sizes_location, min_allowable_size = self._get_REopt_tech_max_sizes_min_turn_down(self.available_techs)
        max_sizes_bau, min_turn_down_bau, max_sizes_location_bau, min_allowable_size_bau = self._get_REopt_tech_max_sizes_min_turn_down(self.bau_techs, bau=True)

        levelization_factor, pwf_e, pwf_om, two_party_factor, \
            pwf_boiler_fuel, pwf_chp_fuel, pwf_fuel_by_tech = self._get_REopt_pwfs(self.available_techs)
        levelization_factor_bau, pwf_e_bau, pwf_om_bau, two_party_factor_bau, \
            pwf_boiler_fuel_bau, pwf_chp_fuel_bau, pwf_fuel_by_tech_bau = self._get_REopt_pwfs(self.bau_techs)
        
        pwf_prod_incent, prod_incent_rate, max_prod_incent, max_size_for_prod_incent, production_incentive_rate  \
            = self._get_REopt_production_incentives(self.available_techs)
        pwf_prod_incent_bau, prod_incent_rate_bau, max_prod_incent_bau, max_size_for_prod_incent_bau, production_incentive_rate_bau \
            = self._get_REopt_production_incentives(self.bau_techs)

        cap_cost_slope, cap_cost_x, cap_cost_yint, n_segments = self._get_REopt_cost_curve(self.available_techs)
        cap_cost_slope_bau, cap_cost_x_bau, cap_cost_yint_bau, n_segments_bau = self._get_REopt_cost_curve(self.bau_techs)
        n_segments_list = [x for x in range(n_segments)]
        n_segments_list_bau = [x for x in range(n_segments_bau)]

        sf = self.site.financial
        StorageCostPerKW = setup_capital_cost_incentive(self.storage.installed_cost_us_dollars_per_kw,  # use full cost as basis
                                                        self.storage.replace_cost_us_dollars_per_kw,
                                                        self.storage.inverter_replacement_year,
                                                        sf.owner_discount_pct,
                                                        sf.owner_tax_pct,
                                                        self.storage.incentives.itc_pct,
                                                        self.storage.incentives.macrs_schedule,
                                                        self.storage.incentives.macrs_bonus_pct,
                                                        self.storage.incentives.macrs_itc_reduction)
        StorageCostPerKW -= self.storage.incentives.rebate
        StorageCostPerKWH = setup_capital_cost_incentive(self.storage.installed_cost_us_dollars_per_kwh,  # there are no cash incentives for kwh
                                                         self.storage.replace_cost_us_dollars_per_kwh,
                                                         self.storage.battery_replacement_year,
                                                         sf.owner_discount_pct,
                                                         sf.owner_tax_pct,
                                                         self.storage.incentives.itc_pct,
                                                         self.storage.incentives.macrs_schedule,
                                                         self.storage.incentives.macrs_bonus_pct,
                                                         self.storage.incentives.macrs_itc_reduction)

        HotTESCostPerMMBTU = setup_capital_cost_incentive(self.hot_tes.installed_cost_us_dollars_per_mmbtu,  # use full cost as basis
                                                        0,
                                                        0,
                                                        sf.owner_discount_pct,
                                                        sf.owner_tax_pct,
                                                        0,
                                                        self.hot_tes.incentives.macrs_schedule,
                                                        self.hot_tes.incentives.macrs_bonus_pct,
                                                        0)

        ColdTESCostPerKWHT = setup_capital_cost_incentive(self.cold_tes.installed_cost_us_dollars_per_kwht,  # use full cost as basis
                                                        0,
                                                        0,
                                                        sf.owner_discount_pct,
                                                        sf.owner_tax_pct,
                                                        0,
                                                        self.cold_tes.incentives.macrs_schedule,
                                                        self.cold_tes.incentives.macrs_bonus_pct,
                                                        0)

        parser = UrdbParse(big_number=big_number, elec_tariff=self.elec_tariff, fuel_tariff=self.fuel_tariff,
                          techs=get_techs_not_none(self.available_techs, self),
                           bau_techs=get_techs_not_none(self.bau_techs, self),
                           loads=self.available_loads, gen=self.generator, chp=eval('self.chp'),
                           boiler=eval('self.boiler'), electric_chiller=eval('self.elecchl'),
                           absorption_chiller=eval('self.absorpchl'))
        tariff_args = parser.parse_rate(self.elec_tariff.utility_name, self.elec_tariff.rate_name)
        TechToNMILMapping, TechsByNMILRegime, NMIL_regime = self._get_REopt_techToNMILMapping(self.available_techs)
        TechToNMILMapping_bau, TechsByNMILRegime_bau, NMIL_regime_bau = self._get_REopt_techToNMILMapping(self.bau_techs)
        if len(NMIL_regime) == 0:
            NMILLimits = []
        else:
            NMILLimits = [self.elec_tariff.net_metering_limit_kw, self.elec_tariff.interconnection_limit_kw,
                      self.elec_tariff.interconnection_limit_kw * 10]
        if len(NMIL_regime_bau) == 0:
            NMILLimits_bau = []
        else:
            NMILLimits_bau = [self.elec_tariff.net_metering_limit_kw, self.elec_tariff.interconnection_limit_kw,
                      self.elec_tariff.interconnection_limit_kw * 10]
        self.year_one_energy_cost_series_us_dollars_per_kwh = parser.energy_rates_summary
        self.year_one_demand_cost_series_us_dollars_per_kw = parser.demand_rates_summary


        subdivisions = ['CapCost']
        fuel_type = ['DIESEL'] if 'GENERATOR' in reopt_techs else []
        fuel_type_bau = ['DIESEL'] if 'GENERATOR' in reopt_techs_bau else []

        # There are no cost curves yet, but incentive size limits and existing techs require cost curve segments
        # TODO: create this array in _get_REopt_cost_curve?
        seg_by_tech_subdivision = list()
        seg_by_tech_subdivision_bau = list()
        for _ in subdivisions:
            for _ in reopt_techs:
                seg_by_tech_subdivision.append(n_segments)
            for  _ in reopt_techs_bau:
                seg_by_tech_subdivision_bau.append(n_segments_bau)

        if len(reopt_techs) == 0:
            techs_by_fuel_type = []
        else:
            techs_by_fuel_type = [['GENERATOR'] if ft == 'DIESEL' else [] for ft in fuel_type]
        if len(reopt_techs_bau) == 0:
            techs_by_fuel_type_bau = []
        else:
            techs_by_fuel_type_bau = [['GENERATOR'] if ft == 'DIESEL' else [] for ft in fuel_type_bau]

        fuel_limit = [0.0 for _ in fuel_type]
        fuel_limit_bau = [0.0 for _ in fuel_type_bau]
        for f in range(len(fuel_type)):
            for t in techs_by_fuel_type[f]:
                tech_idx = reopt_techs.index(t)
                fuel_limit[f] += tariff_args.energy_avail[tech_idx]
        for f in range(len(fuel_type_bau)):
            for t in techs_by_fuel_type_bau[f]:
                tech_idx = reopt_techs_bau.index(t)
                fuel_limit_bau[f] += tariff_args.energy_avail_bau[tech_idx]

        # TODO: switch back to cap_cost_x input since we are just repeating its values?
        segment_min_size = []
        for j in range(0, len(cap_cost_x), n_segments+1):
            for _ in subdivisions:
                for i in range(j, n_segments+j):
                    segment_min_size.append(cap_cost_x[i])

        segment_min_size_bau = []
        for j in range(0, len(cap_cost_x_bau), n_segments_bau+1):
            for _ in subdivisions:
                for i in range(j, n_segments_bau+j):
                    segment_min_size_bau.append(cap_cost_x_bau[i])

        segment_max_size = [] 
        for j in range(0, len(cap_cost_x), n_segments+1):
            for _ in subdivisions:
                for i in range(j, n_segments+j):
                    segment_max_size.append(cap_cost_x[i+1])

        segment_max_size_bau = []
        for j in range(0, len(cap_cost_x_bau), n_segments_bau+1):
            for _ in subdivisions:
                for i in range(j, n_segments_bau+j):
                    segment_max_size_bau.append(cap_cost_x_bau[i+1])

        grid_charge_efficiency = self.storage.rectifier_efficiency_pct * self.storage.internal_efficiency_pct**0.5
        
        fb_techs = [t for t in reopt_techs if t in self.fuel_burning_techs]
        fb_techs_bau = [t for t in reopt_techs_bau if t in self.fuel_burning_techs]
        
        techs_no_turndown = [t for t in reopt_techs if t.startswith("PV") or t.startswith("WIND")]
        techs_no_turndown_bau = [t for t in reopt_techs_bau if t.startswith("PV") or t.startswith("WIND")]
        
        electric_techs = [t for t in reopt_techs if t.startswith("PV") or t.startswith("WIND") or t.startswith("GENERATOR")]
        electric_techs_bau = [t for t in reopt_techs_bau if t.startswith("PV") or t.startswith("WIND") or t.startswith("GENERATOR")]
        
        if len(reopt_techs) > 0:
            non_storage_sales_tiers = [1, 2]
            storage_sales_tiers = [3]
            curtailment_tiers = [3]
            max_grid_sales = self.load.annual_kwh
        else:
            non_storage_sales_tiers = []
            storage_sales_tiers = []
            curtailment_tiers = []
            max_grid_sales = 0
            
        if len(reopt_techs_bau) > 0:
            non_storage_sales_tiers_bau = [1, 2]
            storage_sales_tiers_bau = [3]
            curtailment_tiers_bau = [3]
            max_grid_sales_bau = self.load.annual_kwh
        else:
            non_storage_sales_tiers_bau = []
            storage_sales_tiers_bau = []
            curtailment_tiers_bau = []
            max_grid_sales_bau = 0

        time_steps_with_grid, time_steps_without_grid = self._get_time_steps_with_grid()
        
        self.reopt_inputs = {
            'Tech': reopt_techs,
            'TechToLocation': tech_to_location,
            'MaxSizesLocation': max_sizes_location,
            'TechClass': self.available_tech_classes,
            'TurbineDerate': derate,
            'NMILRegime': NMIL_regime,
            'MaxSize': max_sizes,
            'TechClassMinSize': tech_class_min_size,
            'MinTurndown': min_turn_down,
            'LevelizationFactor': levelization_factor,
            'pwf_e': pwf_e,
            'pwf_om': pwf_om,
            'two_party_factor': two_party_factor,
            'pwf_prod_incent': pwf_prod_incent,
            'MaxProdIncent': max_prod_incent,
            'MaxSizeForProdIncent': max_size_for_prod_incent,
            'CapCostSlope': cap_cost_slope,
            'CapCostX': cap_cost_x,
            'CapCostYInt': cap_cost_yint,
            'r_tax_owner': sf.owner_tax_pct,
            'r_tax_offtaker': sf.offtaker_tax_pct,
            'StorageCostPerKW': StorageCostPerKW,
            'StorageCostPerKWH': StorageCostPerKWH,
            'OMperUnitSize': om_cost_us_dollars_per_kw,
            'OMcostPerUnitProd': om_cost_us_dollars_per_kwh,
            'analysis_years': int(sf.analysis_years),
            'NumRatchets': tariff_args.demand_num_ratchets,
            'FuelBinCount': tariff_args.energy_tiers_num,
            'DemandBinCount': tariff_args.demand_tiers_num,
            'DemandMonthsBinCount': tariff_args.demand_month_tiers_num,
            'DemandRatesMonth': tariff_args.demand_rates_monthly,
            'DemandRates': tariff_args.demand_rates_tou,
            'TimeStepRatchets': tariff_args.demand_ratchets_tou,
            'MaxDemandInTier': tariff_args.demand_max_in_tiers,
            'MaxUsageInTier': tariff_args.energy_max_in_tiers,
            'MaxDemandMonthsInTier': tariff_args.demand_month_max_in_tiers,
            'FuelAvail': tariff_args.energy_avail,
            'FixedMonthlyCharge': tariff_args.fixed_monthly_charge,
            'AnnualMinCharge': tariff_args.annual_min_charge,
            'MonthlyMinCharge': tariff_args.min_monthly_charge,
            'DemandLookbackMonths': tariff_args.demand_lookback_months,
            'DemandLookbackPercent': tariff_args.demand_lookback_percent,
            'TimeStepRatchetsMonth': tariff_args.demand_ratchets_monthly,
            'TimeStepCount': self.n_timesteps,
            'TimeStepScaling': 8760.0 / self.n_timesteps,
            'AnnualElecLoad': self.load.annual_kwh,
            'StorageMinChargePcent': self.storage.soc_min_pct,
            'InitSOC': self.storage.soc_init_pct,
            'NMILLimits': NMILLimits,
            'TechToNMILMapping': TechToNMILMapping,
            'CapCostSegCount': n_segments,
            # new parameters for reformulation
            'StorageCostPerKW': StorageCostPerKW,
	        'StorageCostPerKWH': StorageCostPerKWH,
	        'FuelCost': tariff_args.fuel_costs,
	        'ElecRate': tariff_args.energy_costs,
	        'GridExportRates': tariff_args.grid_export_rates, # seems like the wrong size
	        'FuelBurnSlope': tariff_args.fuel_burn_rate,
	        'FuelBurnYInt': tariff_args.fuel_burn_intercept,
	        'MaxGridSales': max_grid_sales,
	        'ProductionIncentiveRate': production_incentive_rate,
	        'ProductionFactor': production_factor,
	        'ElecLoad': self.load.load_list,
	        'FuelLimit': fuel_limit,
	        'ChargeEfficiency': charge_efficiency, # Do we need this indexed on tech?
	        'GridChargeEfficiency': grid_charge_efficiency,
	        'DischargeEfficiency': discharge_efficiency,
	        'StorageMinSizeEnergy': self.storage.min_kwh,
	        'StorageMaxSizeEnergy': self.storage.max_kwh,
	        'StorageMinSizePower': self.storage.min_kw,
	        'StorageMaxSizePower': self.storage.max_kw,
	        'StorageMinSOC': self.storage.soc_min_pct,
	        'StorageInitSOC': self.storage.soc_init_pct,
            'SegmentMinSize': segment_min_size,
            'SegmentMaxSize': segment_max_size,
            # Sets that need to be populated
            'Storage': ['Elec'],
            'FuelType': fuel_type,
            'Subdivision': subdivisions,
            'PricingTierCount': tariff_args.energy_tiers_num,
            'ElecStorage': ['Elec'],
            'SegByTechSubdivision': seg_by_tech_subdivision,
            'TechsInClass': techs_in_class,
            'TechsByFuelType': techs_by_fuel_type,
            'ElectricTechs': electric_techs,
            'FuelBurningTechs': fb_techs,
            'TechsNoTurndown': techs_no_turndown,
            'SalesTierCount': tariff_args.num_sales_tiers,
            'StorageSalesTiers': storage_sales_tiers,
            'NonStorageSalesTiers': non_storage_sales_tiers,
            'TimeStepsWithGrid': time_steps_with_grid,
            'TimeStepsWithoutGrid': time_steps_without_grid,
            'SalesTiersByTech': tariff_args.rates_by_tech,
            'TechsBySalesTier':tariff_args.techs_by_rate,
            'CurtailmentTiers':curtailment_tiers,
            'ElectricDerate':electric_derate,
            'TechsByNMILRegime':TechsByNMILRegime
            }

        self.reopt_inputs_bau = {
            'Tech': reopt_techs_bau,
            'TechToLocation': tech_to_location_bau,
            'MaxSizesLocation': max_sizes_location_bau,
            'TechClass': self.available_tech_classes,
            'NMILRegime': NMIL_regime_bau,
            'TurbineDerate': derate_bau,
            'MaxSize': max_sizes_bau,
            'TechClassMinSize': tech_class_min_size_bau,
            'MinTurndown': min_turn_down_bau,
            'LevelizationFactor': levelization_factor_bau,
            'pwf_e': pwf_e_bau,
            'pwf_om': pwf_om_bau,
            'two_party_factor': two_party_factor_bau,
            'pwf_prod_incent': pwf_prod_incent_bau,
            'MaxProdIncent': max_prod_incent_bau,
            'MaxSizeForProdIncent': max_size_for_prod_incent_bau,
            'CapCostSlope': cap_cost_slope_bau,
            'CapCostX': cap_cost_x_bau,
            'CapCostYInt': cap_cost_yint_bau,
            'r_tax_owner': sf.owner_tax_pct,
            'r_tax_offtaker': sf.offtaker_tax_pct,
            'StorageCostPerKW': StorageCostPerKW,
            'StorageCostPerKWH': StorageCostPerKWH,
            'OMperUnitSize': om_dollars_per_kw_bau,
            'OMcostPerUnitProd': om_dollars_per_kwh_bau,
            'analysis_years': int(sf.analysis_years),
            'NumRatchets': tariff_args.demand_num_ratchets,
            'FuelBinCount': tariff_args.energy_tiers_num,
            'DemandBinCount': tariff_args.demand_tiers_num,
            'DemandMonthsBinCount': tariff_args.demand_month_tiers_num,
            'DemandRatesMonth': tariff_args.demand_rates_monthly,
            'DemandRates': tariff_args.demand_rates_tou,
            'TimeStepRatchets': tariff_args.demand_ratchets_tou,
            'MaxDemandInTier': tariff_args.demand_max_in_tiers,
            'MaxUsageInTier': tariff_args.energy_max_in_tiers,
            'MaxDemandMonthsInTier': tariff_args.demand_month_max_in_tiers,
            'FuelAvail': tariff_args.energy_avail_bau,
            'FixedMonthlyCharge': tariff_args.fixed_monthly_charge,
            'AnnualMinCharge': tariff_args.annual_min_charge,
            'MonthlyMinCharge': tariff_args.min_monthly_charge,
            'DemandLookbackMonths': tariff_args.demand_lookback_months,
            'DemandLookbackPercent': tariff_args.demand_lookback_percent,
            'TimeStepRatchetsMonth': tariff_args.demand_ratchets_monthly,
            'TimeStepCount': self.n_timesteps,
            'TimeStepScaling': 8760.0 / self.n_timesteps,
            'AnnualElecLoad': self.load.annual_kwh,
            'StorageMinChargePcent': self.storage.soc_min_pct,
            'InitSOC': self.storage.soc_init_pct,
            'NMILLimits': NMILLimits_bau,
            'TechToNMILMapping': TechToNMILMapping_bau,
            'CapCostSegCount': n_segments_bau,
            # new parameters for reformulation
            'StorageCostPerKW': StorageCostPerKW,
	        'StorageCostPerKWH': StorageCostPerKWH,
	        'FuelCost': tariff_args.fuel_costs_bau,
	        'ElecRate': tariff_args.energy_costs_bau,
	        'GridExportRates': tariff_args.grid_export_rates_bau,
	        'FuelBurnSlope': tariff_args.fuel_burn_rate_bau,
	        'FuelBurnYInt': tariff_args.fuel_burn_intercept_bau,
	        'MaxGridSales': max_grid_sales_bau,
	        'ProductionIncentiveRate': production_incentive_rate_bau,
	        'ProductionFactor': production_factor_bau,
	        'ElecLoad': self.load.bau_load_list,
	        'FuelLimit': fuel_limit_bau,
	        'ChargeEfficiency': charge_efficiency_bau,
	        'GridChargeEfficiency': grid_charge_efficiency,
	        'DischargeEfficiency': discharge_efficiency_bau,
	        'StorageMinSizeEnergy':0,
	        'StorageMaxSizeEnergy':0,
	        'StorageMinSizePower':0,
	        'StorageMaxSizePower':0,
	        'StorageMinSOC':self.storage.soc_min_pct,
	        'StorageInitSOC':self.storage.soc_init_pct,
            'SegmentMinSize':segment_min_size_bau,
            'SegmentMaxSize':segment_max_size_bau,
            # Sets that need to be populated
            'Storage':['Elec'],
            'FuelType':fuel_type_bau,
            'Subdivision':subdivisions,
            'PricingTierCount':tariff_args.energy_tiers_num,
            'ElecStorage':[],
            'SegByTechSubdivision':seg_by_tech_subdivision_bau,
            'TechsInClass':techs_in_class_bau,
            'TechsByFuelType':techs_by_fuel_type_bau,
            'ElectricTechs':electric_techs_bau,
            'FuelBurningTechs':fb_techs_bau,
            'TechsNoTurndown':techs_no_turndown_bau,
            'SalesTierCount':tariff_args.num_sales_tiers_bau,
            'StorageSalesTiers':storage_sales_tiers_bau,
            'NonStorageSalesTiers':non_storage_sales_tiers_bau,
            'TimeStepsWithGrid':time_steps_with_grid,
            'TimeStepsWithoutGrid':time_steps_without_grid,
            'SalesTiersByTech': tariff_args.rates_by_tech_bau,
            'TechsBySalesTier':tariff_args.techs_by_rate_bau,
            'CurtailmentTiers':curtailment_tiers_bau,
            'ElectricDerate':electric_derate_bau,
            'TechsByNMILRegime':TechsByNMILRegime_bau
        }
