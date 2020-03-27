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
from reo.utilities import annuity, annuity_degr, degradation_factor, slope, intercept, insert_p_after_u_bp, insert_p_bp, \
    insert_u_after_p_bp, insert_u_bp, setup_capital_cost_incentive
max_incentive = 1.0e10

big_number = 1.0e10
squarefeet_to_acre = 2.2957e-5


def get_techs_not_none(techs, cls):
    ret = []
    for tech in techs:
        if eval('cls.' + tech) is not None:
            ret.append(tech)
    return ret


class DatFileManager:
    """
    Creates input dicts for reopt.jl and manages data transfer between Celery tasks
    """

    def __init__(self, run_id, n_timesteps=8760):
        self.pv = None
        self.pvnm = None
        self.wind = None
        self.windnm = None
        self.generator = None
        self.util = None
        self.storage = None
        self.site = None
        self.elec_tariff = None
        self.load = None
        self.reopt_inputs = None
        self.reopt_inputs_bau = None

        # following attributes used to pass data to process_results.py
        self.LoadProfile = {}
        self.year_one_energy_cost_series_us_dollars_per_kwh = []
        self.year_one_demand_cost_series_us_dollars_per_kw = []

        self.available_techs = ['pv', 'pvnm', 'wind', 'windnm', 'generator', 'util']  # order is critical for REopt!
        self.available_tech_classes = ['PV', 'WIND', 'GENERATOR', 'UTIL']  # this is a REopt 'class', not a python class
        self.available_loads = ['retail', 'wholesale', 'export', 'storage']  # order is critical for REopt!
        self.bau_techs = ['util']
        self.NMILRegime = ['BelowNM', 'NMtoIL', 'AboveIL']

        self.run_id = run_id
        self.n_timesteps = n_timesteps
        self.pwf_e = 0  # used in results.py -> outage_costs.py to escalate & discount avoided outage costs

    def add_load(self, load):
        #  fill in W, X, S bins
        for _ in range(self.n_timesteps * 3):
            load.load_list.append(big_number)
            load.bau_load_list.append(big_number)
        self.LoadProfile["critical_load_series_kw"] = load.critical_load_series_kw
        self.LoadProfile["resilience_check_flag"] = load.resilience_check_flag
        self.LoadProfile["sustain_hours"] = load.sustain_hours
        self.LoadProfile["annual_kwh"] = load.annual_kwh
        self.load = load

    def add_pv(self, pv):
        junk = pv.prod_factor  # avoids redundant PVWatts call for pvnm
        self.pv = pv
        self.pvnm = copy.deepcopy(pv)
        self.pvnm.nmil_regime = 'NMtoIL'

        if self.pv.existing_kw > 0:
            tmp_tech = ['pv', 'pvnm']
            self.bau_techs = tmp_tech+self.bau_techs

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

    def add_site(self, site):
        self.site = site

    def add_storage(self, storage):
        self.storage = storage
        # storage_bau.dat gets same definitions as storage.dat so that initializations don't fail in bau case
        # however, storage is typically 'turned off' by having max size set to zero in maxsizes_bau.dat
        # TODO: save reopt_inputs dictionary?
        # efficiencies are defined in finalize method because their arrays depend on which Techs are defined

    def add_elec_tariff(self, elec_tariff):
        self.elec_tariff = elec_tariff

    def _get_REopt_pwfs(self, techs):

        sf = self.site.financial
        pwf_owner = annuity(sf.analysis_years, 0, sf.owner_discount_pct) # not used in REopt
        pwf_offtaker = annuity(sf.analysis_years, 0, sf.offtaker_discount_pct)  # not used in REopt
        pwf_om = annuity(sf.analysis_years, sf.om_cost_escalation_pct, sf.owner_discount_pct)
        pwf_e = annuity(sf.analysis_years, sf.escalation_pct, sf.offtaker_discount_pct)
        self.pwf_e = pwf_e
        # pwf_op = annuity(sf.analysis_years, sf.escalation_pct, sf.owner_discount_pct)

        if pwf_owner == 0 or sf.owner_tax_pct == 0:
            two_party_factor = 0
        else:
            two_party_factor = (pwf_offtaker * sf.offtaker_tax_pct) \
                                / (pwf_owner * sf.owner_tax_pct)

        levelization_factor = list()
        production_incentive_levelization_factor = list()

        for tech in techs:

            if eval('self.' + tech) is not None:

                if tech in ['pv', 'pvnm']:  # pv has degradation

                    #################
                    # NOTE: I don't think that levelization factors should include an escalation rate.  The degradation
                    # does not escalate in out years.
                    ################
                    degradation_pct = eval('self.' + tech + '.degradation_pct')
                    levelization_factor.append(round(degradation_factor(sf.analysis_years, degradation_pct), 5))
                    production_incentive_levelization_factor.append(
                        round(degradation_factor(eval('self.' + tech + '.incentives.production_based.years'),
                                                 degradation_pct), 5))
                    ################
                else:

                    levelization_factor.append(1.0)
                    production_incentive_levelization_factor.append(1.0)

        return levelization_factor, production_incentive_levelization_factor, pwf_e, pwf_om, two_party_factor

    def _get_REopt_production_incentives(self, techs):

        sf = self.site.financial
        pwf_prod_incent = list()
        prod_incent_rate = list()
        max_prod_incent = list()
        max_size_for_prod_incent = list()

        for tech in techs:

            if eval('self.' + tech) is not None:

                if tech not in ['util', 'generator']:

                    # prod incentives don't need escalation
                    pwf_prod_incent.append(
                        annuity(eval('self.' + tech + '.incentives.production_based.years'),
                                0, sf.offtaker_discount_pct)
                    )
                    max_prod_incent.append(
                        eval('self.' + tech + '.incentives.production_based.max_us_dollars_per_kw')
                    )
                    max_size_for_prod_incent.append(
                        eval('self.' + tech + '.incentives.production_based.max_kw')
                    )

                    for load in self.available_loads:
                        prod_incent_rate.append(
                            eval('self.' + tech + '.incentives.production_based.us_dollars_per_kw')
                        )

                else:

                    pwf_prod_incent.append(0.0)
                    max_prod_incent.append(0.0)
                    max_size_for_prod_incent.append(0.0)

                    for load in self.available_loads:
                        prod_incent_rate.append(0.0)

        return pwf_prod_incent, prod_incent_rate, max_prod_incent, max_size_for_prod_incent

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

            if eval('self.' + tech) is not None and tech not in ['util']:

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
                    updated_slope = setup_capital_cost_incentive(itc_unit_basis,  # input tech cost with incentives, but no ITC
                                                                 0,
                                                                 sf.analysis_years,
                                                                 sf.owner_discount_pct,
                                                                 sf.owner_tax_pct,
                                                                 itc,
                                                                 eval('self.' + tech + '.incentives.macrs_schedule'),
                                                                 eval('self.' + tech + '.incentives.macrs_bonus_pct'),
                                                                 eval('self.' + tech + '.incentives.macrs_itc_reduction'))

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

            elif eval('self.' + tech) is not None and tech in ['util']:

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

        for tech in techs:

            if eval('self.' + tech) is not None:

                tech_regime = eval('self.' + tech + '.nmil_regime')

                for regime in self.NMILRegime:
                    if regime == tech_regime:
                        TechToNMILMapping.append(1)
                    else:
                        TechToNMILMapping.append(0)
        return TechToNMILMapping

    def _get_REopt_array_tech_load(self, techs):
        """
        Many arrays are built from Tech and Load. As many as possible are defined here to reduce for-loop iterations
        :param techs: list of strings, eg. ['pv', 'pvnm', 'util']
        :return: prod_factor, tech_to_load, tech_is_grid, derate, etaStorIn, etaStorOut
        """
        prod_factor = list()
        tech_to_load = list()
        tech_is_grid = list()
        derate = list()
        eta_storage_in = list()
        eta_storage_out = list()
        om_cost_us_dollars_per_kw = list()
        om_cost_us_dollars_per_kwh = list()

        for tech in techs:

            if eval('self.' + tech) is not None:

                tech_is_grid.append(int(eval('self.' + tech + '.is_grid')))
                derate.append(eval('self.' + tech + '.derate'))
                om_cost_us_dollars_per_kw.append(float(eval('self.' + tech + '.om_cost_us_dollars_per_kw')))

                # only generator tech has variable o&m cost
                if tech.lower() == 'generator':
                    om_cost_us_dollars_per_kwh.append(float(eval('self.' + tech + '.kwargs["om_cost_us_dollars_per_kwh"]')))
                else:
                    om_cost_us_dollars_per_kwh.append(0.0)

                for load in self.available_loads:

                    eta_storage_in.append(self.storage.rectifier_efficiency_pct *
                                          self.storage.internal_efficiency_pct**0.5 if load == 'storage' else float(1))

                    if eval('self.' + tech + '.can_serve(' + '"' + load + '"' + ')'):

                        for pf in eval('self.' + tech + '.prod_factor'):
                            prod_factor.append(float(pf))

                        tech_to_load.append(1)

                    else:

                        for _ in range(self.n_timesteps):
                            prod_factor.append(float(0.0))

                        tech_to_load.append(0)

                    # By default, util can serve storage load.
                    # However, if storage is being modeled it can override grid-charging
                    if tech == 'util' and load == 'storage' and self.storage is not None:
                        tech_to_load[-1] = int(self.storage.canGridCharge)

        for load in self.available_loads:
            # eta_storage_out is array(Load) of real
            eta_storage_out.append(self.storage.inverter_efficiency_pct * self.storage.internal_efficiency_pct**0.5
                                   if load == 'storage' else 1.0)

        # In BAU case, storage.dat must be filled out for REopt initializations, but max size is set to zero

        return prod_factor, tech_to_load, tech_is_grid, derate, eta_storage_in, eta_storage_out, \
               om_cost_us_dollars_per_kw, om_cost_us_dollars_per_kwh

    def _get_REopt_techs(self, techs):
        reopt_techs = list()
        for tech in techs:

            if eval('self.' + tech) is not None:

                reopt_techs.append(tech.upper() if tech is not 'util' else tech.upper() + '1')

        return reopt_techs

    def _get_REopt_tech_classes(self, techs, bau):
        """

        :param techs: list of strings, eg. ['pv', 'pvnm', 'util']
        :return: tech_classes, tech_class_min_size, tech_to_tech_class
        """
        tech_class_min_size = list()  # array(TechClass)
        tech_to_tech_class = list()  # array(Tech, TechClass)
        for tc in self.available_tech_classes:
            if eval('self.' + tc.lower()) is not None and tc.lower() in techs:
                if hasattr(eval('self.' + tc.lower()), 'existing_kw'):
                    if bau:
                        new_value = (eval('self.' + tc.lower() + '.existing_kw') or 0.0)
                    else:
                        new_value = (eval('self.' + tc.lower() + '.existing_kw') or 0.0) + (eval('self.' + tc.lower() + '.min_kw') or 0.0)
                else:
                    new_value = (eval('self.' + tc.lower() + '.min_kw') or 0.0)
                tech_class_min_size.append(new_value)
            else:
                tech_class_min_size.append(0.0)

        for tech in techs:

            if eval('self.' + tech) is not None:

                for tc in self.available_tech_classes:

                    if eval('self.' + tech + '.reopt_class').upper() == tc.upper():
                        tech_to_tech_class.append(1)
                    else:
                        tech_to_tech_class.append(0)


        return tech_class_min_size, tech_to_tech_class

    def _get_REopt_tech_max_sizes_min_turn_down(self, techs, bau=False):
        max_sizes = list()
        min_turn_down = list()
        for tech in techs:

            if eval('self.' + tech) is not None:
                existing_kw = 0.0
                if hasattr(eval('self.' + tech), 'existing_kw'):
                    if eval('self.' + tech + '.existing_kw') is not None:
                        existing_kw = eval('self.' + tech + '.existing_kw')

                if hasattr(eval('self.' + tech), 'min_turn_down'):
                    min_turn_down.append(eval('self.' + tech + '.min_turn_down'))
                else:
                    min_turn_down.append(0.0)

                beyond_existing_cap_kw = eval('self.' + tech + '.max_kw')
                if eval('self.' + tech + '.acres_per_kw') is not None:
                    if eval('self.' + tech + '.kw_per_square_foot') is not None:
                        if self.site.roof_squarefeet is not None and self.site.land_acres is not None:
                            # don't restrict unless they specify both land_area and roof_area,
                            # otherwise one of them is "unlimited" in UI
                            roof_max_kw = self.site.roof_squarefeet * eval('self.' + tech + '.kw_per_square_foot')
                            land_max_kw = self.site.land_acres / eval('self.' + tech + '.acres_per_kw')
                            beyond_existing_cap_kw = min(roof_max_kw + land_max_kw, beyond_existing_cap_kw)

                if bau and existing_kw > 0:  # existing PV in BAU scenario
                    max_sizes.append(float(existing_kw))
                else:
                    max_sizes.append(float(existing_kw + beyond_existing_cap_kw))

        return max_sizes, min_turn_down

    def finalize(self):
        """
        necessary for writing out parameters that depend on which Techs are defined
        eg. in REopt ProdFactor: array (Tech,Load,TimeStep).
        Note: whether or not a given Tech can serve a given Load can also be controlled via TechToLoadMatrix
        :return: None
        """
        reopt_techs = self._get_REopt_techs(self.available_techs)
        reopt_techs_bau = self._get_REopt_techs(self.bau_techs)

        load_list = ['1R', '1W', '1X', '1S']  # same for BAU

        tech_class_min_size, tech_to_tech_class = self._get_REopt_tech_classes(self.available_techs, False)
        tech_class_min_size_bau, tech_to_tech_class_bau = self._get_REopt_tech_classes(self.bau_techs, True)

        prod_factor, tech_to_load, tech_is_grid, derate, eta_storage_in, eta_storage_out, om_cost_us_dollars_per_kw,\
            om_cost_us_dollars_per_kwh= self._get_REopt_array_tech_load(self.available_techs)
        prod_factor_bau, tech_to_load_bau, tech_is_grid_bau, derate_bau, eta_storage_in_bau, eta_storage_out_bau, \
            om_dollars_per_kw_bau, om_dollars_per_kwh_bau = self._get_REopt_array_tech_load(self.bau_techs)

        max_sizes, min_turn_down = self._get_REopt_tech_max_sizes_min_turn_down(self.available_techs)
        max_sizes_bau, min_turn_down_bau = self._get_REopt_tech_max_sizes_min_turn_down(self.bau_techs, bau=True)

        levelization_factor, production_incentive_levelization_factor, pwf_e, pwf_om, two_party_factor \
            = self._get_REopt_pwfs(self.available_techs)
        levelization_factor_bau, production_incentive_levelization_factor_bau, pwf_e_bau, pwf_om_bau, two_party_factor_bau \
            = self._get_REopt_pwfs(self.bau_techs)

        pwf_prod_incent, prod_incent_rate, max_prod_incent, max_size_for_prod_incent \
            = self._get_REopt_production_incentives(self.available_techs)
        pwf_prod_incent_bau, prod_incent_rate_bau, max_prod_incent_bau, max_size_for_prod_incent_bau \
            = self._get_REopt_production_incentives(self.bau_techs)

        cap_cost_slope, cap_cost_x, cap_cost_yint, n_segments = self._get_REopt_cost_curve(self.available_techs)
        cap_cost_slope_bau, cap_cost_x_bau, cap_cost_yint_bau, n_segments_bau = self._get_REopt_cost_curve(self.bau_techs)

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

        parser = UrdbParse(big_number=big_number, elec_tariff=self.elec_tariff,
                           techs=get_techs_not_none(self.available_techs, self),
                           bau_techs=get_techs_not_none(self.bau_techs, self),
                           loads=self.available_loads, gen=self.generator)
        tariff_args = parser.parse_rate(self.elec_tariff.utility_name, self.elec_tariff.rate_name)
        TechToNMILMapping = self._get_REopt_techToNMILMapping(self.available_techs)
        TechToNMILMapping_bau = self._get_REopt_techToNMILMapping(self.bau_techs)
        NMILLimits = [self.elec_tariff.net_metering_limit_kw, self.elec_tariff.interconnection_limit_kw,
                      self.elec_tariff.interconnection_limit_kw * 10]
        self.year_one_energy_cost_series_us_dollars_per_kwh = parser.energy_rates_summary
        self.year_one_demand_cost_series_us_dollars_per_kw = parser.demand_rates_summary

        self.reopt_inputs = {
            'Tech': reopt_techs,
            'Load': load_list,
            'TechClass': self.available_tech_classes,
            'TechIsGrid': tech_is_grid,
            'TechToLoadMatrix': tech_to_load,
            'TurbineDerate': derate,
            'TechToTechClassMatrix': tech_to_tech_class,
            'NMILRegime': self.NMILRegime,
            'ProdFactor': prod_factor,
            'EtaStorIn': eta_storage_in,
            'EtaStorOut': eta_storage_out,
            'MaxSize': max_sizes,
            'MinStorageSizeKW': self.storage.min_kw,
            'MaxStorageSizeKW': self.storage.max_kw,
            'MinStorageSizeKWH': self.storage.min_kwh,
            'MaxStorageSizeKWH': self.storage.max_kwh,
            'TechClassMinSize': tech_class_min_size,
            'MinTurndown': min_turn_down,
            'LevelizationFactor': levelization_factor,
            'LevelizationFactorProdIncent': production_incentive_levelization_factor,
            'pwf_e': pwf_e,
            'pwf_om': pwf_om,
            'two_party_factor': two_party_factor,
            'pwf_prod_incent': pwf_prod_incent,
            'ProdIncentRate': prod_incent_rate,
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
            # 'MinDemand': tariff_args.demand_min  # not used in REopt,
            'TimeStepRatchets': tariff_args.demand_ratchets_tou,
            'MaxDemandInTier': tariff_args.demand_max_in_tiers,
            'MaxUsageInTier': tariff_args.energy_max_in_tiers,
            'MaxDemandMonthsInTier': tariff_args.demand_month_max_in_tiers,
            'FuelRate': tariff_args.energy_rates,
            'FuelAvail': tariff_args.energy_avail,
            'FixedMonthlyCharge': tariff_args.fixed_monthly_charge,
            'AnnualMinCharge': tariff_args.annual_min_charge,
            'MonthlyMinCharge': tariff_args.min_monthly_charge,
            'ExportRates': tariff_args.export_rates,
            'DemandLookbackMonths': tariff_args.demand_lookback_months,
            'DemandLookbackPercent': tariff_args.demand_lookback_percent,
            'TimeStepRatchetsMonth': tariff_args.demand_ratchets_monthly,
            'FuelBurnRateM': tariff_args.energy_burn_rate,
            'FuelBurnRateB': tariff_args.energy_burn_intercept,
            'TimeStepCount': self.n_timesteps,
            'TimeStepScaling': 8760.0 / self.n_timesteps,
            'AnnualElecLoad': self.load.annual_kwh,
            'LoadProfile': self.load.load_list,
            'StorageMinChargePcent': self.storage.soc_min_pct,
            'InitSOC': self.storage.soc_init_pct,
            'NMILLimits': NMILLimits,
            'TechToNMILMapping': TechToNMILMapping,
            'CapCostSegCount': n_segments,
            # new parameters for reformulation
            'StoragePowerCost': 0,
					 'StorageEnergyCost': 0,
					 'FuelCost': 0,
					 'ElecRate': 0,
					 'GridExportRates': 0,
					 'FuelBurnSlope': 0,
					 'FueBurnYInt': 0,
					 'MaxGridSales': 0,
					 'ProductionIncentiveRate': 0,
					 'ProductionFactor': 0,
					 'ElecLoad': 0,
					 'FuelLimit': 0,
					 'ChargeEfficiency': 0,
					 'GridChargeEfficiency': 0,
					 'DischargeEfficiency': 0,
		  'StorageMinSizeEnergy':0,
		  'StorageMaxSizeEnergy':0,
		  'StorageMinSizePower':0,
		  'StorageMaxSizePower':0,
		  'StorageMinSOC':0,
		  'StorageInitSOC':0,
            #'BattLevelCoef':
            #'BattLevelCount':
            #'Points':
            #'Month':
            #'Ratchets':
            #'FuelBin':
            #'DemandBin':
            #'DemandMonthsBin':
            #'BattLevel':
            #'TimeStep':
            #'TimeStepBat':
        }
        self.reopt_inputs_bau = {
            'Tech': reopt_techs_bau,
            'TechIsGrid': tech_is_grid_bau,
            'Load': load_list,
            'TechToLoadMatrix': tech_to_load_bau,
            'TechClass': self.available_tech_classes,
            'NMILRegime': self.NMILRegime,
            'TurbineDerate': derate_bau,
            'TechToTechClassMatrix': tech_to_tech_class_bau,
            'ProdFactor': prod_factor_bau,
            'EtaStorIn': eta_storage_in_bau,
            'EtaStorOut': eta_storage_out_bau,
            'MaxSize': max_sizes_bau,
            'MinStorageSizeKW': 0.0,
            'MaxStorageSizeKW': 0.0,
            'MinStorageSizeKWH': 0.0,
            'MaxStorageSizeKWH': 0.0,
            'TechClassMinSize': tech_class_min_size_bau,
            'MinTurndown': min_turn_down_bau,
            'LevelizationFactor': levelization_factor_bau,
            'LevelizationFactorProdIncent': production_incentive_levelization_factor_bau,
            'pwf_e': pwf_e_bau,
            'pwf_om': pwf_om_bau,
            'two_party_factor': two_party_factor_bau,
            'pwf_prod_incent': pwf_prod_incent_bau,
            'ProdIncentRate': prod_incent_rate_bau,
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
            # 'MinDemand': tariff_args.demand_min  # not used in REopt,
            'TimeStepRatchets': tariff_args.demand_ratchets_tou,
            'MaxDemandInTier': tariff_args.demand_max_in_tiers,
            'MaxUsageInTier': tariff_args.energy_max_in_tiers,
            'MaxDemandMonthsInTier': tariff_args.demand_month_max_in_tiers,
            'FuelRate': tariff_args.energy_rates_bau,
            'FuelAvail': tariff_args.energy_avail_bau,
            'FixedMonthlyCharge': tariff_args.fixed_monthly_charge,
            'AnnualMinCharge': tariff_args.annual_min_charge,
            'MonthlyMinCharge': tariff_args.min_monthly_charge,
            'ExportRates': tariff_args.export_rates_bau,
            'DemandLookbackMonths': tariff_args.demand_lookback_months,
            'DemandLookbackPercent': tariff_args.demand_lookback_percent,
            'TimeStepRatchetsMonth': tariff_args.demand_ratchets_monthly,
            'FuelBurnRateM': tariff_args.energy_burn_rate_bau,
            'FuelBurnRateB': tariff_args.energy_burn_intercept_bau,
            'TimeStepCount': self.n_timesteps,
            'TimeStepScaling': 8760.0 / self.n_timesteps,
            'AnnualElecLoad': self.load.annual_kwh,
            'LoadProfile': self.load.bau_load_list,
            'StorageMinChargePcent': self.storage.soc_min_pct,
            'InitSOC': self.storage.soc_init_pct,
            'NMILLimits': NMILLimits,
            'TechToNMILMapping': TechToNMILMapping_bau,
            'CapCostSegCount': n_segments_bau,
            # new parameters for reformulation
            'StoragePowerCost': 0,
					 'StorageEnergyCost': 0,
					 'FuelCost': 0,
					 'ElecRate': 0,
					 'GridExportRates': 0,
					 'FuelBurnSlope': 0,
					 'FueBurnYInt': 0,
					 'MaxGridSales': 0,
					 'ProductionIncentiveRate': 0,
					 'ProductionFactor': 0,
					 'ElecLoad': 0,
					 'FuelLimit': 0,
					 'ChargeEfficiency': 0,
					 'GridChargeEfficiency': 0,
					 'DischargeEfficiency': 0,
		  'StorageMinSizeEnergy':0,
		  'StorageMaxSizeEnergy':0,
		  'StorageMinSizePower':0,
		  'StorageMaxSizePower':0,
		  'StorageMinSOC':0,
		  'StorageInitSOC':0,
        }
