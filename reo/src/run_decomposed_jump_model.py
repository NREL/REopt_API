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
from celery import shared_task, Task, chain, group, chord
from reo.exceptions import REoptError, OptimizationTimeout, UnexpectedError, NotOptimal, REoptFailedToStartError,\
    CheckGapException
from reo.models import ModelManager
from reo.src.profiler import Profiler
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


@shared_task(bind=True, base=RunDecomposedJumpModelTask)
def run_decomposed_jump_model(self, dfm_bau, data):
    """
    Run after BAU scenario, passes [dfm, dfm_bau] to process_results,
    where the dfm is a copy of dfm_bau with results from decomposed JuMP model in dfm['results']
    :param self:
    :param dfm_bau:
    :param data:
    :param run_uuid:
    :return:
    """
    profiler = Profiler()
    time_dict = dict()

    self.data = data
    self.run_uuid = data['outputs']['Scenario']['run_uuid']
    self.user_uuid = data['outputs']['Scenario'].get('user_uuid')

    julia_img_file = get_julia_img_file_name()

    logger.info("Running JuMP model ...")

    t_start = time.time()
    if os.path.isfile(julia_img_file):
        logger.info("Found Julia image file {}.".format(julia_img_file))
        api = LibJulia.load()
        api.sysimage = julia_img_file
        api.init_julia()
    else:
        j = julia.Julia()
    time_dict["pyjulia_start_seconds"] = time.time() - t_start

    solver = os.environ.get("SOLVER")

    data["lb_iters"] = 3
    data["max_iters"] = 100
    data["solver"] = solver
    data["lb"] = -1.0e100
    data["ub"] = 1.0e100
    data["run_uuid"] = self.run_uuid
    data["user_uuid"] = self.user_uuid

    data["t_start"] = time.time()

    run_subproblems.s(dfm_bau, data)()


"""
setup | run_decomposed_jump_model

run_decomposed_jump_model sets up all inputs to and starts a recursive run_subproblems task that kicks off a 
    chain(group(subproblems) | checktol().onerror(run_decomposed_problem) | process_results)
    
checktol dfm -> process_results
    call_back = process_results.s(data=data, meta={'run_uuid': run_uuid, 'api_version': api_version})

"""
@shared_task
def run_subproblems(request_or_dfm, data_or_exc, traceback=None):
    logger.warn("run_subproblems traceback: {}".format(traceback))
    if not isinstance(data_or_exc, dict):
        if not isinstance(data_or_exc, CheckGapException):
            raise data_or_exc # not handled correctly
        lb_update = True
        dfm_bau = data_or_exc.dfm_bau
        data = data_or_exc.data
        data["iter"] = data_or_exc.iter
        logger.info("iter {} of run_subproblems".format(data["iter"]))
    else:
        lb_update = False
        logger.info("first iter of run_subproblems")
        dfm_bau = request_or_dfm
        data = data_or_exc
        data["start_timestamp"] = time.time()
        data["iter"] = 0
        data["penalties"] = [{} for _ in range(12)]

    data["lb_result_dicts"] = [{} for _ in range(12)]
    data["ub_result_dicts"] = [{} for _ in range(12)]
    max_size = (data["iter"] == 1)
    lb_group = lb_subproblems_group.s(data["solver"], dfm_bau["reopt_inputs"], data["penalties"], lb_update,
                                      data["lb_result_dicts"], data["run_uuid"], data["user_uuid"])
    lb_result = chord(lb_group())(store_lb_results.s(data))
    wait_for_group_results("lb", lb_result)  # blocking process
    data = lb_result.result  # data gets replaced several times in this function, really hard to follow
    lb_result.forget()  # what does forget do? releases resources from a task
    # can we run lb_group and ub_group together? If so then they can be a part of the chain with checkgap ?
    ub_group = ub_subproblems_group.s(data["solver"], dfm_bau["reopt_inputs"], max_size, data["iter_size_summary"],
                                      data["iter_mean_sizes"], data["run_uuid"], data["user_uuid"])
    ub_result = chord(ub_group())(store_ub_results.s(data, dfm_bau["reopt_inputs"]))
    wait_for_group_results("ub", ub_result)  # blocking process
    data = ub_result.result
    ub_result.forget()
    callback = checkgap.s(dfm_bau, data)

    chain(callback.on_error(run_subproblems.s()) |
          process_results.s(data=data, meta={'run_uuid': data['outputs']['Scenario']['run_uuid'],
                                           'api_version': "v1"}
                          )
          )()
    return "subproblems running iteration {}".format(data["iter"])


@shared_task
def checkgap(dfm_bau, data):
    iter = data["iter"]
    time_limit = data["inputs"]["Scenario"]["timeout_seconds"]
    opt_tolerance = data["inputs"]["Scenario"]["optimality_tolerance"]
    lb_result_dicts = data["lb_result_dicts"]
    lb = sum([lb_result_dicts[m]["lower_bound"] for m in range(12)])
    if lb > data["lb"]:
        data["lb"] = lb
    ub_result_dicts = data["ub_result_dicts"]

    if data["iter_ub"] < data["ub"]:
        data["best_result_dicts"] = copy.deepcopy(ub_result_dicts)
        data["min_charge_adder"] = data["iter_min_charge_adder"]
        data["ub"] = data["iter_ub"]
    gap = abs((data["ub"] - data["lb"]) / data["lb"])
    logger.info("Gap: {}".format(gap))
    max_iters = data["max_iters"]
    elapsed_time = time.time() - data["start_timestamp"]

    if (gap >= 0. and gap <= opt_tolerance) or (iter >= max_iters) or (elapsed_time > time_limit):
        results = aggregate_submodel_results(dfm_bau['reopt_inputs'], data["best_result_dicts"], data["ub"], data["min_charge_adder"])
        dfm = copy.deepcopy(dfm_bau)
        dfm["results"] = results
        return [dfm, dfm_bau]  # -> process_results

    else:  # kick off recursive run_subproblems
        data["iter"] += 1
        raise CheckGapException(dfm_bau, data)  # -> callback.on_error -> run_subproblems


@shared_task
def store_lb_results(results, data):
    """
    Call back for lb_subproblems_group
    :param results:  list of dicts, length = 12
    :param data:  dict
    :return data:  dict updated with LB subproblem results as new key-val pairs
    """
    for i in range(12):
        data["lb_result_dicts"][i] = copy.deepcopy(results[i])
    size_summary = get_size_summary(data["lb_result_dicts"])
    mean_sizes = get_average_sizing_decisions(size_summary)
    data["iter_size_summary"] = size_summary
    data["iter_mean_sizes"] = mean_sizes
    data["penalties"] = update_penalties(data["penalties"], size_summary, mean_sizes, 1.0e-4)
    return data


@shared_task
def store_ub_results(results, data, reopt_inputs):
    """
     Call back for ub_subproblems_group
    :param results:  list of dicts, length = 12
    :param data:  dict
    :param reopt_inputs: dict of julia inputs
    :return data: dict updated with UB subproblem results as new key-val pairs
    """
    for i in range(12):
        data["ub_result_dicts"][i] = copy.deepcopy(results[i])
    ub, min_charge_adder, prod_incentives = get_objective_value(data["ub_result_dicts"], reopt_inputs)
    data["iter_ub"] = ub
    data["iter_min_charge_adder"] = min_charge_adder
    data["iter_prod_incentives"] = prod_incentives
    return data


@shared_task
def ub_subproblems_group(solver, reopt_inputs, max_size, size_summary, mean_sizes, run_uuid,
                         user_uuid):
    """
    Creates, builds and solves subproblems in Julia
    :param lb_result_dicts: string identifier of solver
    :param solver: string identifier of solver
    :param reopt_inputs: inputs dictionary from DataManger
    :param max_size: Boolean that is True if using the max size of each system, and False if using average size
    :param size_summary: list of dicts, length=12; contains system sizes and reset inventory levels
    :param mean_sizes: dictionary containsin average size of each system
    :param run_uuid:  String - run identifier
    :param user_uuid: String - user identifier
    :return: celery group in which the result of eah member is a Julia subproblem results dictionary
    """
    if max_size:
        fixed_sizes = get_max_sizing_decisions(size_summary)
    else:
        fixed_sizes = mean_sizes
    return group(solve_ub_subproblem.s({
        "solver": solver,
        "inputs": reopt_inputs,
        "month": mth,
        "sizes": fixed_sizes["system_sizes"],
        "power": fixed_sizes["storage_power"],
        "energy": fixed_sizes["storage_energy"],
        "inv": fixed_sizes["storage_inv"],
        "run_uuid": run_uuid,
        "user_uuid": user_uuid
    }) for mth in range(1, 13))

@shared_task
def lb_subproblems_group(solver, reopt_inputs, penalties, update, results, run_uuid, user_uuid):
    """
    Creates, builds and solves subproblems in Julia
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
        "results": results[mth-1],
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
    from julia import Main
    from julia import Pkg
    activate_julia_env(sp_dict["solver"], Pkg, sp_dict["run_uuid"], sp_dict["user_uuid"])
    if sp_dict["solver"] == "xpress":
        Main.include("reo/src/reopt_xpress_model.jl")
    elif sp_dict["solver"] == "cbc":
        Main.include("reo/src/reopt_cbc_model.jl")
    elif sp_dict["solver"] == "scip":
        Main.include("reo/src/reopt_scip_model.jl")
    Main.include("reo/src/reopt_decomposed.jl")

    results = Main.reopt_lb_subproblem(sp_dict["solver"], sp_dict["inputs"], sp_dict["month"], sp_dict["penalties"],
                                       sp_dict["update"])
    sp_dict["results"] = results
    return results

@shared_task
def solve_ub_subproblem(sp_dict):
    """
    Run solve_ub_subproblem Julia method
    :param sp_dict: subproblem input dict
    :return: updated sp_dict with sp_dict["results"] containing latest results
    """
    from julia import Main
    from julia import Pkg
    activate_julia_env(sp_dict["solver"], Pkg, sp_dict["run_uuid"], sp_dict["user_uuid"])
    Main.include("reo/src/reopt_decomposed.jl")

    results = Main.reopt_ub_subproblem(sp_dict["solver"], sp_dict["inputs"], sp_dict["month"], sp_dict["sizes"],
                                       sp_dict["power"], sp_dict["energy"], sp_dict["inv"])
    sp_dict["results"] = results
    return results


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
    size_summary = {
        "system_sizes": [],
        "storage_power": [],
        "storage_energy": [],
        "storage_inv": []
    }
    for i in range(12):
        s = str(lb_result_dicts[i])
        r = lb_result_dicts[i]
        size_summary["system_sizes"].append(r["system_sizes"])
        size_summary["storage_power"].append(r["storage_power"])
        size_summary["storage_energy"].append(r["storage_energy"])
        size_summary["storage_inv"].append(r["storage_inv"])
    return size_summary


def get_average_sizing_decisions(size_summary):
    avg_sizes = {}
    for key in size_summary.keys():
        avg_sizes[key] = copy.deepcopy(size_summary[key][0])
    for i in range(1, 12):
        for key1 in size_summary.keys():
            for key2 in size_summary[key1][i].keys():
                avg_sizes[key1][key2] += size_summary[key1][i][key2]
    for key1 in size_summary.keys():
        for key2 in size_summary[key1][i].keys():
            avg_sizes[key1][key2] /= 12.
    return avg_sizes


def get_max_sizing_decisions(size_summary):
    max_sizes = {}
    for key in size_summary.keys():
        max_sizes[key] = copy.deepcopy(size_summary[key][0])
    for i in range(1, 12):
        for key1 in size_summary.keys():
            for key2 in size_summary[key1][i].keys():
                max_sizes[key1][key2] = max(max_sizes[key1][key2], size_summary[key1][i][key2])
    return max_sizes


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
    :param min_charge_adder:
    :return:
    """
    from julia import Main
    from julia import Pkg
    run_uuid = ""  # TODO
    user_uuid = ""  # TODO
    activate_julia_env(os.environ.get("SOLVER"), Pkg, run_uuid, user_uuid)
    Main.include("reo/src/reopt_decomposed.jl")
    results = Main.aggregate_results(reopt_inputs, ub_results)
    results["lcc"] = lcc
    results["total_min_charge_adder"] = min_charge_adder
    results["year_one_min_charge_adder"] = min_charge_adder / reopt_inputs["pwf_e"]
    return results


def wait_for_group_results(probs, result):
    while True:
        if result.status == "SUCCESS":
            logger.info("subproblem group completed.")
            return None
        elif result.status == "PENDING" or result.status == "STARTED":
            time.sleep(2)
        else:
            logger.info("Unsuccessful execution of subproblem group occurred.")
            raise UnexpectedError("Failed group result.", None, None)
            return None
