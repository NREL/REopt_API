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
    from julia import Main
    time_dict["pyjulia_start_seconds"] = time.time() - t_start

    t_start = time.time()
    Main.using("Pkg")
    from julia import Pkg
    time_dict["pyjulia_pkg_seconds"] = time.time() - t_start

    solver = os.environ.get("SOLVER")

    t_start = time.time()
    activate_julia_env(solver, Pkg, self.run_uuid, self.user_uuid)
    time_dict["pyjulia_activate_seconds"] = time.time() - t_start

    model, time_dict = get_julia_model(solver, time_dict, Pkg, Main, self.run_uuid, self.user_uuid, data)

    t_start = time.time()
    Main.include("reo/src/reopt_decomposed.jl")
    time_dict["pyjulia_include_reopt_seconds"] = time.time() - t_start

    data["lb_iters"] = 3
    data["max_iters"] = 100
    data["model"] = model
    data["solver"] = solver

    data["lb_models"] = {}
    data["ub_models"] = {}
    data["lb_results"] = {}
    data["ub_results"] = {}
    data["penalties"] = {}
    data["system_sizes"] = {}

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

    if not isinstance(data_or_exc, dict):
        update = True
        dfm_bau = data_or_exc.dfm_bau
        data = data_or_exc.data
        data["iter"] = data_or_exc.iter
        logger.info("iter {} of run_subproblems".format(data["iter"]))
    else:
        logger.info("first iter of run_subproblems")
        update = False
        dfm_bau = request_or_dfm
        data = data_or_exc
        data["iter"] = 1
        data["lb_result_dicts"] = {}
        data["ub_result_dicts"] = {}
        data["penalties"] = {}

    update = (data["iter"] == 1)
    lb_group = lb_subproblems_group(dfm_bau["reopt_inputs"], data["penalties"], update)
    ub_group = ub_subproblems_group(dfm_bau["reopt_inputs"], data["lb_result_dicts"], data["system_sizes"], update)
    callback = checkgap.s(dfm_bau, data)

    chain(lb_group | ub_group | callback.on_error(run_subproblems.s()) |
          process_results.s(data=data, meta={'run_uuid': data['outputs']['Scenario']['run_uuid'],
                                           'api_version': "v1"}
                          )
          )()
    return "subproblems running iteration {}".format(data["iter"])


@shared_task
def checkgap(grp_results, dfm_bau, data):
    iter = data["iter"]
    time_limit = data["inputs"]["Scenario"]["timeout_seconds"]
    opt_tolerance = data["inputs"]["Scenario"]["optimality_tolerance"]

    lb_result_dicts = grp_results[0:12]
    lb = sum([lb_result_dicts[m]["lower_bound"] for m in range(1, 13)])
    fix_sizing_decisions(data["ub_models"], data["reopt_param"], system_sizes)

    ub_result_dicts = grp_results[12:24]
    best_result_dicts = copy.deepcopy(ub_result_dicts)
    ub, min_charge_adder, prod_incentives = get_objective_value(ub_result_dicts, dfm_bau['reopt_inputs'])
    gap = (ub - lb) / lb
    logger.info("Gap: {}".format(gap))
    lb_iters = data["lb_iters"]
    max_iters = data["max_iters"]
    model = data["model"]

    if gap <= opt_tolerance or iter >= 2: #max_iters:  # or time or iterations
        results = aggregate_submodel_results(best_result_dicts, ub, min_charge_adder, dfm_bau['reopt_inputs']["pwf_e"])
        results = julia.Main.convert_to_axis_arrays(data["reopt_param"], results)
        dfm = copy.deepcopy(data["dfm_bau"])
        dfm["results"] = results
        return [dfm, data["dfm_bau"]]  # -> process_results

    else:  # kick off recursive run_subproblems
        raise CheckGapException(dfm_bau, data)  # -> callback.on_error -> run_subproblems


def build_submodels(models, reopt_param):
    result_dicts = {}
    for idx in range(1, 13):
        result_dicts[idx] = julia.Main.reopt_build(models[idx], reopt_param)
    return result_dicts

def ub_subproblems_group(lb_results, solver, reopt_inputs, update):

def lb_subproblems_group(solver, reopt_inputs, penalties, update):
    """
    Solves subproblems
    :param models: dictionary in which key=month (1=Jan, 12=Dec) and values are JuMP model objects
    :param reopt_param: Julia Parameter struct
    :param results_dicts: dictionary in which key=month and vals are submodel results dictionaries
    :param update: Boolean that is True if skipping the creation of output expressions, and False o.w.
    :return: celery group
    """
    return group(solve_lb_subproblem.s({
        "m": models[mth],
        "p": reopt_param,
        "r": results_dicts[mth],
        "u": update,
        "month": mth
    }) for mth in range(1, 13))


@shared_task
def solve_lb_subproblem(sp_dict):
    """
    Run solve_lb_subproblem Julia method
    :param sp_dict: subproblem input dict
    :return: updated sp_dict with sp_dict["r"] containing latest results
    """
    results = julia.Main.reopt_lb_subproblem(sp_dict["solver"], sp_dict["inputs"], sp_dict["month"], sp_dict["penalties"], sp_dict["update"])
    return results

@shared_task
def solve_ub_subproblem(sp_dict):
    """
    Run solve_ub_subproblem Julia method
    :param sp_dict: subproblem input dict
    :return: updated sp_dict with sp_dict["r"] containing latest results
    """
    results = julia.Main.reopt_ub_subproblem(sp_dict["solver"], sp_dict["inputs"], sp_dict["month"], sp_dict["sizes"], sp_dict["update"])
    return results


def fix_sizing_decisions(ub_models, reopt_param, system_sizes):
    for i in range(1, 13):
        julia.Main.fix_sizing_decisions(ub_models[i], reopt_param, system_sizes)


def get_objective_value(ub_result_dicts, reopt_inputs):
    """
    Calculates the full-year problem objective value by adjusting
    year-long components as required.
    :param ub_result_dicts: subproblem results dictionaries
    :param reopt_inputs: inputs dictionary from DataManager
    :return obj:  full-year objective value
    :return prod_incentives: list of production incentive by technology
    :return min_charge_adder: calculated annual minimum charge adder
    """
    obj = sum([ub_result_dicts[idx]["obj_no_annuals"] for idx in range(1, 13)])
    min_charge_comp = sum([ub_result_dicts[idx]["min_charge_adder_comp"] for idx in range(1, 13)])
    total_min_charge = sum([ub_result_dicts[idx]["total_min_charge"] for idx in range(1, 13)])
    min_charge_adder = max(0, total_min_charge - min_charge_comp)
    obj += min_charge_adder
    prod_incentives = []
    for tech_idx in range(len(reopt_inputs['Tech'])):
        max_prod_incent = reopt_inputs['MaxProdIncent'][tech_idx] * reopt_inputs['pwf_prod_incent'][tech_idx] * reopt_inputs['two_party_factor']
        prod_incent = sum([ub_result_dicts[idx]["sub_incentive"][tech_idx] for idx in range(1, 13)])
        prod_incentive = min(prod_incent, max_prod_incent)
        obj += prod_incentive
        prod_incentives.append(prod_incentive)
    if len(reopt_inputs['DemandLookbackMonths']) > 0 and reopt_inputs['DemandLookbackPercent'] > 0.0:
        obj += get_added_peak_tou_costs(ub_result_dicts, reopt_inputs)
    return obj, min_charge_adder, prod_incentives


def get_added_peak_tou_costs(ub_result_dicts, reopt_inputs):
    """
    Calculated added TOU costs to according to peak lookback months.
    :param ub_result_dicts:
    :param reopt_inputs:
    :return:
    """
    added_obj = 0.
    max_lookback_val = ub_result_dicts[1]["peak_demand_for_month"] if 1 in reopt_inputs['DemandLookbackMonths'] else 0.0
    peak_ratchets = ub_result_dicts[1]["peak_ratchets"]
    for m in range(2, 13):
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


def get_average_sizing_decisions(models, reopt_param):
    sizes = julia.Main.get_sizing_decisions(models[1], reopt_param)
    for i in range(2, 13):
        d = julia.Main.get_sizing_decisions(models[i], reopt_param)
        for key in d.keys():
            sizes[key] += d[key]
    for key in d.keys():
        sizes[key] /= 12.
    return sizes


def aggregate_submodel_results(ub_results, obj, min_charge_adder, pwf_e):
    results = ub_results[1]
    for idx in range(2, 13):
        results = julia.Main.add_to_results(results, ub_results[idx])
    results["lcc"] = obj
    results["total_min_charge_adder"] = min_charge_adder
    results["year_one_min_charge_adder"] = min_charge_adder / pwf_e
    return results
