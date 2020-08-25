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
import julia
import sys
import traceback
import os
from celery import shared_task, Task, chain, group
from reo.exceptions import REoptError, OptimizationTimeout, UnexpectedError, NotOptimal, REoptFailedToStartError,\
    CheckGapException
from reo.models import ModelManager
from celery.utils.log import get_task_logger
from julia.api import LibJulia
from reo.utilities import get_julia_img_file_name, activate_julia_env, get_julia_model
from reo.process_results import process_results
import time
import copy
import numpy
# julia.install()  # needs to be run if it is the first time you are using julia package
logger = get_task_logger(__name__)


class RunDecomposedJumpModelTask(Task):
    """
    Used to define custom Error handling for celery task
    """
    name = 'run_decomposed_jump_model'
    max_retries = 0

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        log a bunch of stuff for debugging
        save message: error and outputs: Scenario: status
        :param exc: The exception raised by the task.
        :param task_id: Unique id of the failed task. (not the run_uuid)
        :param args: Original arguments for the task that failed.
        :param kwargs: Original keyword arguments for the task that failed.
        :param einfo: ExceptionInfo instance, containing the traceback.
        :return: None, The return value of this handler is ignored.
        """
        if isinstance(exc, REoptError):
            exc.save_to_db()
            msg = exc.message
        else:
            msg = exc.args[0]
        data = kwargs['data']
        data["messages"]["error"] = msg
        data["outputs"]["Scenario"]["status"] = "An error occurred. See messages for more."
        ModelManager.update_scenario_and_messages(data, run_uuid=data['outputs']['Scenario']['run_uuid'])

        self.request.chain = None  # stop the chain
        self.request.callback = None
        self.request.chord = None  # this seems to stop the infinite chord_unlock call


@shared_task(base=RunDecomposedJumpModelTask)
def run_decomposed_jump_model(dfm_bau, data):
    """
    Run after BAU scenario, set up inputs to run_subproblems, a recursive task that calls itself if checkgap fails
    :param dfm_bau: dfm from run_jump_model for BAU scenario, also used to pass results between upper and lower subproblems
    :param data: nested dict mirroring API response format
    :return: None
    """
    logger.info("Running JuMP model ...")
    decomp_data = dict()  # for managing problem decomposition, passing data between problems
    decomp_data["lb_iters"] = 3
    decomp_data["max_iters"] = 100
    decomp_data["solver"] = os.environ.get("SOLVER")
    decomp_data["lb"] = -1.0e100
    decomp_data["ub"] = 1.0e100
    decomp_data["timeout_seconds"] = data["inputs"]["Scenario"]["timeout_seconds"]
    decomp_data["opt_tolerance"] = data["inputs"]["Scenario"]["optimality_tolerance"]
    decomp_data["run_uuid"] = data['outputs']['Scenario']['run_uuid']
    decomp_data["user_uuid"] = data['outputs']['Scenario'].get('user_uuid')
    decomp_data["post_process_signature"] = process_results.s(data=data, meta={'run_uuid': decomp_data["run_uuid"], 'api_version': "v1"})
    run_subproblems.s(dfm_bau, decomp_data)()


@shared_task
def run_subproblems(request_or_dfm, dd_or_exc, traceback=None):
    """
    group(lb_problems) | store_lb_results | group(ub_problems) | store_ub_results | checkgap | process_results
    :param request_or_dfm: dfm on first call, celery.app.task.Context thereafter
    :param dd_or_exc: dict on first call, CheckGapException thereafter
    :param traceback: None on first call, traceback from .on_error thereafter
    :return: "subproblems running iteration {}".format(dd["iter"])
    """
    logger.warn("run_subproblems traceback: {}".format(traceback))
    if not isinstance(dd_or_exc, dict):
        if not isinstance(dd_or_exc, CheckGapException):
            raise dd_or_exc  # TODO not handled correctly, reuse on_failure from RunDecomposedJumpModelTask ?
        update_lb = True
        dfm_bau = dd_or_exc.dfm_bau
        dd = dd_or_exc.data
        dd["iter"] = dd_or_exc.iter
        logger.info("iter {} of run_subproblems".format(dd["iter"]))
    else:
        update_lb = False
        logger.info("first iter of run_subproblems")
        dfm_bau = request_or_dfm
        dd = dd_or_exc
        dd["start_timestamp"] = time.time()
        dd["iter"] = 0
        dd["penalties"] = [{} for _ in range(12)]

    max_size = (dd["iter"] == 1)
    lb_group = lb_subproblems_group(dd["solver"], dfm_bau["reopt_inputs"], dd["penalties"], update_lb,
                                    dd["run_uuid"], dd["user_uuid"])
    lb_callback = store_lb_results.s(dd)

    ub_group = group(solve_ub_subproblem.s(max_size, month, dfm_bau["reopt_inputs"]) for month in range(1, 13))
    ub_callback = store_ub_results.s(dfm_bau["reopt_inputs"])

    gapcheck = checkgap.s(dfm_bau)

    chain(lb_group | lb_callback | ub_group | ub_callback | gapcheck.on_error(run_subproblems.s()) |
          dd["post_process_signature"])()

    return "subproblems running iteration {}".format(dd["iter"])


def lb_subproblems_group(solver, reopt_inputs, penalties, update, run_uuid, user_uuid):
    """
    Creates a group of monthly lower-bound subproblems
    :param solver: dictionary in which key=month (1=Jan, 12=Dec) and values are JuMP model objects
    :param reopt_inputs: inputs dictionary from DataManger
    :param penalties: Lagrangian penalties for different system sizes (key=month index)
    :param update: Boolean that is True if skipping the creation of output expressions, and False o.w.
    :return: celery group
    """
    return group(solve_lb_subproblem.s({
        "solver": solver,
        "inputs": reopt_inputs,
        "month": mth,
        "penalties": penalties[mth - 1],
        "update": update,
        "run_uuid": run_uuid,
        "user_uuid": user_uuid
    }) for mth in range(1, 13))


@shared_task
def solve_lb_subproblem(sp_dict):
    """
    Run solve_lb_subproblem Julia method
    :param sp_dict: subproblem input dict
    :return: updated sp_dict with sp_dict["results"] containing latest results
    """
    init_julia()
    from julia import Main  # global Main does not work in celery tasks :(
    from julia import Pkg
    activate_julia_env(sp_dict["solver"], Pkg, sp_dict["run_uuid"], sp_dict["user_uuid"])
    # why don't we need these if/else statements in solve_ub_subproblem? can we eliminate them here?
    if sp_dict["solver"] == "xpress":
        Main.include("reo/src/reopt_xpress_model.jl")
    elif sp_dict["solver"] == "cbc":
        Main.include("reo/src/reopt_cbc_model.jl")
    elif sp_dict["solver"] == "scip":
        Main.include("reo/src/reopt_scip_model.jl")
    Main.include("reo/src/reopt_decomposed.jl")

    results = Main.reopt_lb_subproblem(sp_dict["solver"], sp_dict["inputs"], sp_dict["month"], sp_dict["penalties"],
                                       sp_dict["update"])
    return results  # list of results -> store_lb_results


@shared_task
def store_lb_results(results, dd):
    """
    Call back for lb_subproblems_group
    :param results: list of dicts, length = 12
    :param dd: dict
    :return dd: dict updated with LB subproblem results as new key-val pairs
    """
    dd["lb_result_dicts"] = results
    size_summary = get_size_summary(dd["lb_result_dicts"])
    mean_sizes, max_sizes = get_average_max_sizing_decisions(size_summary)
    dd["iter_size_summary"] = size_summary
    dd["iter_mean_sizes"] = mean_sizes
    dd["iter_max_sizes"] = max_sizes
    dd["penalties"] = update_penalties(dd["penalties"], size_summary, mean_sizes, 1.0e-4)
    return dd  # -> group(solve_ub_subproblem's)


@shared_task
def solve_ub_subproblem(dd, max_size, month, reopt_inputs):
    """
    Run reopt_ub_subproblem Julia method from reopt_decomposed.jl
    Run in group after store_lb_results
    :param dd: updated decomp_params dict from store_lb_results
    :return: updated decomp_params dict with ub problem results
    """
    if max_size:
        fixed_sizes = dd["iter_max_sizes"]
    else:
        fixed_sizes = dd["iter_mean_sizes"]

    init_julia()
    from julia import Main
    from julia import Pkg
    activate_julia_env(dd["solver"], Pkg, dd["run_uuid"], dd["user_uuid"])
    Main.include("reo/src/reopt_decomposed.jl")

    results = Main.reopt_ub_subproblem(dd["solver"], reopt_inputs, month, fixed_sizes["system_sizes"],
                                       fixed_sizes["storage_power"], fixed_sizes["storage_energy"], fixed_sizes["storage_inv"])
    dd["ubresults"] = results
    return dd  # -> list of dd's to store_ub_results


@shared_task
def store_ub_results(dds, reopt_inputs):
    """
     Call back for ub_subproblems_group
    :param dds: list of decomp_params dicts, length = 12, including lb and ub results
    :param reopt_inputs: dict of julia inputs
    :return dd: dict updated with UB subproblem results as new key-val pairs
    """
    dd = dds[0]
    dd["ub_result_dicts"] = [dds[month]["ubresults"] for month in range(12)]
    ub, min_charge_adder, prod_incentives = get_objective_value(dd["ub_result_dicts"], reopt_inputs)
    dd["iter_ub"] = ub
    dd["iter_min_charge_adder"] = min_charge_adder
    dd["iter_prod_incentives"] = prod_incentives
    return dd  # -> checkgap


@shared_task
def checkgap(dd, dfm_bau):
    lb = sum([dd["lb_result_dicts"][m]["lower_bound"] for m in range(12)])
    if lb > dd["lb"]:
        dd["lb"] = lb
    ub_result_dicts = dd["ub_result_dicts"]

    if dd["iter_ub"] < dd["ub"]:
        dd["best_result_dicts"] = copy.deepcopy(ub_result_dicts)
        dd["min_charge_adder"] = dd["iter_min_charge_adder"]
        dd["ub"] = dd["iter_ub"]
    gap = abs((dd["ub"] - dd["lb"]) / dd["lb"])
    logger.info("Gap: {}".format(gap))
    elapsed_time = time.time() - dd["start_timestamp"]

    if (gap >= 0. and gap <= dd["opt_tolerance"]) or (dd["iter"] >= dd["max_iters"]) or (elapsed_time > dd["timeout_seconds"]):
        results = aggregate_submodel_results(dfm_bau['reopt_inputs'], dd["best_result_dicts"], dd["ub"], dd["min_charge_adder"])
        dfm = copy.deepcopy(dfm_bau)
        dfm["results"] = results
        return [dfm, dfm_bau]  # -> process_results

    else:  # kick off recursive run_subproblems
        dd["iter"] += 1
        raise CheckGapException(dfm_bau, dd)  # -> callback.on_error -> run_subproblems


def get_objective_value(ub_result_dicts, reopt_inputs):
    """
    Calculates the full-year problem objective value by adjusting
    year-long components as required.
    :param ub_result_dicts: list of subproblem results dictionaries
    :param reopt_inputs: inputs dictionary from DataManager
    :return obj:  full-year objective value
    :return prod_incentives: list of production incentive by technology
    :return min_charge_adder: calculated annual minimum charge adder
    """
    obj = sum([ub_result_dicts[idx]["obj_no_annuals"] for idx in range(12)])
    min_charge_comp = sum([ub_result_dicts[idx]["min_charge_adder_comp"] for idx in range(12)])
    total_min_charge = sum([ub_result_dicts[idx]["total_min_charge"] for idx in range(12)])
    min_charge_adder = max(0, total_min_charge - min_charge_comp)
    obj += min_charge_adder
    prod_incentives = []
    for tech_idx in range(len(reopt_inputs['Tech'])):
        max_prod_incent = reopt_inputs['MaxProdIncent'][tech_idx] * reopt_inputs['pwf_prod_incent'][tech_idx] * reopt_inputs['two_party_factor']
        prod_incent = sum([ub_result_dicts[idx]["sub_incentive"][tech_idx] for idx in range(12)])
        prod_incentive = min(prod_incent, max_prod_incent)
        obj -= prod_incentive
        prod_incentives.append(prod_incentive)
    if len(reopt_inputs['DemandLookbackMonths']) > 0 and reopt_inputs['DemandLookbackPercent'] > 0.0:
        obj += get_added_peak_tou_costs(ub_result_dicts, reopt_inputs)
    return obj, min_charge_adder, prod_incentives


def get_added_peak_tou_costs(ub_result_dicts, reopt_inputs):
    """
    Calculated added TOU costs to according to peak lookback months.
    :param ub_result_dicts: list of dicts (length = 12) containing UB subproblem results
    :param reopt_inputs: dict containing inputs to Julia models (used to populate Julai parameter)
    :return added_obj: float indicating added objective value due to peak tou costs
    """
    added_obj = 0.
    max_lookback_val = ub_result_dicts[0]["peak_demand_for_month"] if 1 in reopt_inputs['DemandLookbackMonths'] else 0.0
    peak_ratchets = ub_result_dicts[0]["peak_ratchets"]
    for m in range(1, 12):
        #update max ratchet purchases
        peak_ratchets = numpy.maximum(peak_ratchets, ub_result_dicts[1]["peak_ratchets"])
        #Update Demandlookback months if required
        if m in reopt_inputs["DemandLookbackMonths"]:
            max_lookback_val = max(max_lookback_val, ub_result_dicts[m]["peak_demand_for_month"])
    #update any ratchet if it is less than the appropriate value
    if all(peak_ratchets >= max_lookback_val * reopt_inputs["DemandLookbackPercent"]):
        return 0.
    for r in range(reopt_inputs["NumRatchets"]):
        if peak_ratchets[r] >= max_lookback_val * reopt_inputs["DemandLookbackPercent"]:
            added_demand = peak_ratchets[r] - max_lookback_val * reopt_inputs["DemandLookbackPercent"]
            bins, vals = get_added_demand_by_bin(peak_ratchets[r], added_demand, reopt_inputs["MaxDemandInBin"])
            for idx in range(len(bins)):
                added_obj += reopt_inputs["DemandRates"][idx*reopt_inputs["NumRatchets"]+bins[idx]] * vals[idx]
    return added_obj


def get_added_demand_by_bin(start, added_demand, max_demand_by_bin):
    """
    obtains added demand by bin for calculation of additional ratchet
    charges when rolling up year-long costs while accounting for
    demand lookback months.
    :param start:  starting peak ratchet demand
    :param added_demand: amount of excess demand to add
    :param bin_maxes: list of bin_maxes
    :return bins: list of bin indices (start at zero)
    :return vals: list of additional value by bin
    """
    excess_remaining = added_demand
    start_remaining = start
    bins = []
    vals = []
    for idx in range(len(max_demand_by_bin)):
        if excess_remaining == 0. and start_remaining == 0.:
            break
        bin_remaining = max_demand_by_bin[idx]
        if bin_remaining > start_remaining:
            bin_remaining -= start_remaining
            start_remaining = 0.
        else:
            start_remaining -= bin_remaining
            continue
        bins.append(idx)
        if bin_remaining >= excess_remaining:
            bin_remaining -= excess_remaining
            vals.append(excess_remaining)
            excess_remaining = 0.
        else:
            excess_remaining -= bin_remaining
            vals.append(bin_remaining)
    return bins, vals


def get_size_summary(lb_result_dicts):
    size_summary = dict()
    size_summary["system_sizes"] = [lb_result_dicts[i]["system_sizes"] for i in range(12)]  # keys ['BOILER', 'CHP']
    size_summary["storage_power"] = [lb_result_dicts[i]["storage_power"] for i in range(12)]  # keys ['ColdTES', 'HotTES', 'Elec'])
    size_summary["storage_energy"] = [lb_result_dicts[i]["storage_energy"] for i in range(12)]
    size_summary["storage_inv"] = [lb_result_dicts[i]["storage_inv"] for i in range(12)]
    return size_summary  # dict of lists of dicts


def get_average_max_sizing_decisions(size_summary):
    """
    Calculate average and max sizes over each monthly problem
    :param size_summary: dict of lists of dicts with:
        - top level keys: dict_keys(['system_sizes', 'storage_power', 'storage_energy', 'storage_inv'])
        - 12 entries in each list (for each month)
        - bottom level keys vary by top key, wiht all storage values having ['ColdTES', 'HotTES', 'Elec']
            and system_sizes: ['BOILER', 'CHP']
    :return: avg_sizes, max_sizes, dicts of dicts, with top and lower level keys matching size_summary keys
    """
    avg_sizes = {}
    max_sizes = {}
    for key in size_summary.keys():
        avg_sizes[key] = copy.copy(size_summary[key][0])
        max_sizes[key] = copy.copy(size_summary[key][0])
    for i in range(1, 12):
        for key1 in size_summary.keys():
            for key2 in size_summary[key1][i].keys():
                avg_sizes[key1][key2] += size_summary[key1][i][key2]
                max_sizes[key1][key2] = max(max_sizes[key1][key2], size_summary[key1][i][key2])
    for key1 in avg_sizes.keys():
        for key2 in avg_sizes[key1].keys():
            avg_sizes[key1][key2] /= 12.
    return avg_sizes, max_sizes


def update_penalties(penalties, size_summary, mean_sizes, rho=1.0e-4):
    # Initialize penalties dictionary if required
    if len(penalties[0]) == 0:
        for i in range(12):
            for key1 in mean_sizes.keys():
                penalties[i][key1] = {}
                for key2 in mean_sizes[key1].keys():
                    penalties[i][key1][key2] = 0.0
    # update values according to difference in system sizes.  These are multiplied by other constants in Julia but are
    # set up so that the sum of each tech-specific penalty across all subproblem is zero.
    for i in range(12):
        for key1 in mean_sizes.keys():
            for key2 in mean_sizes[key1].keys():
                penalties[i][key1][key2] += rho * (size_summary[key1][i][key2] - mean_sizes[key1][key2])
    return penalties


def aggregate_submodel_results(reopt_inputs, ub_results, lcc, min_charge_adder):
    """

    :param reopt_inputs: dict
    :param ub_results: list of dicts, length = 12
    :param lcc: float
    :param min_charge_adder: float
    :return:
    """
    nonPV_size_keys = ["chp_kw","batt_kwh","batt_kw","hot_tes_size_mmbtu","cold_tes_size_kwht",
                       "wind_kw","generator_kw","absorpchl_kw"]
    results = ub_results[0]
    for key in ["obj_no_annuals", "min_charge_adder_comp", "sub_incentive", "peak_demand_for_month", "peak_ratchets",
                "total_min_charge"]:  # delete unnecessary values
        results.pop(key, None)
    for mth in range(1,12):
        for key in results.keys():
            if isinstance(results[key], (float, int)):
                if not key in nonPV_size_keys:
                    if (not "pv" in key) or ((not "PV" in key) and (not "kw" in key)):
                        results[key] += ub_results[mth][key]
            elif isinstance(results[key], list):
                if len(ub_results[mth][key]) >= 672:  # 28 * 24
                    results[key] += ub_results[mth][key]

    results["lcc"] = lcc
    results["total_min_charge_adder"] = min_charge_adder
    results["year_one_min_charge_adder"] = min_charge_adder / reopt_inputs["pwf_e"]
    return results


def init_julia():
    julia_img_file = get_julia_img_file_name()
    if os.path.isfile(julia_img_file):
        logger.info("Found Julia image file {}.".format(julia_img_file))
        api = LibJulia.load()
        api.sysimage = julia_img_file
        api.init_julia()
    else:
        julia.Julia()
