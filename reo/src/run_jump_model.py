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
from celery import shared_task, Task, group
from reo.exceptions import REoptError, OptimizationTimeout, UnexpectedError, NotOptimal, REoptFailedToStartError
from reo.models import ModelManager
from reo.src.profiler import Profiler
from celery.utils.log import get_task_logger
from julia.api import LibJulia
from reo.utilities import get_julia_img_file_name, activate_julia_env, get_julia_model
import time
import copy
import numpy
# julia.install()  # needs to be run if it is the first time you are using julia package
logger = get_task_logger(__name__)


class RunJumpModelTask(Task):
    """
    Used to define custom Error handling for celery task
    """
    name = 'run_jump_model'
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


@shared_task(bind=True, base=RunJumpModelTask)
def run_jump_model(self, dfm, data, run_uuid, bau=False):
    profiler = Profiler()
    time_dict = dict()
    name = 'reopt' if not bau else 'reopt_bau'
    reopt_inputs = dfm['reopt_inputs'] if not bau else dfm['reopt_inputs_bau']
    self.data = data
    self.run_uuid = data['outputs']['Scenario']['run_uuid']
    self.user_uuid = data['outputs']['Scenario'].get('user_uuid')

    julia_img_file = get_julia_img_file_name()

    logger.info("Running JuMP model ...")
    try:
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
        activate_julia_env(solver, time_dict, Pkg, self.run_uuid, self.user_uuid)
        model = get_julia_model(solver, time_dict, Pkg, Main, run_uuid, self.user_uuid, data)

        if len(reopt_inputs["CHPTechs"]) == 0:
            t_start = time.time()
            Main.include("reo/src/reopt.jl")
            time_dict["pyjulia_include_reopt_seconds"] = time.time() - t_start

            t_start = time.time()
            results = Main.reopt(model, reopt_inputs)
            time_dict["pyjulia_run_reopt_seconds"] = time.time() - t_start
        else:
            t_start = time.time()
            Main.include("reo/src/reopt_decomposed.jl")
            time_dict["pyjulia_include_reopt_seconds"] = time.time() - t_start

            t_start = time.time()
            results = run_decomposed_model(data, model, reopt_inputs)
            time_dict["pyjulia_run_reopt_seconds"] = time.time() - t_start

        results.update(time_dict)

    except Exception as e:
        if isinstance(e, REoptFailedToStartError):
            raise e
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(exc_type)
        print(exc_value)
        print(exc_traceback)
        logger.error("REopt.py raise unexpected error: UUID: " + str(self.run_uuid))
        raise UnexpectedError(exc_type, exc_value, traceback.format_tb(exc_traceback), task=name, run_uuid=self.run_uuid, user_uuid=self.user_uuid)
    else:
        status = results["status"]
        logger.info("REopt run successful. Status {}".format(status))
        if bau:
            dfm['results_bau'] = results  # will be flat dict
        else:
            dfm['results'] = results

        if status.strip().lower() == 'timed-out':
            msg = "Optimization exceeded timeout: {} seconds.".format(data["inputs"]["Scenario"]["timeout_seconds"])
            logger.info(msg)
            raise OptimizationTimeout(task=name, message=msg, run_uuid=self.run_uuid, user_uuid=self.user_uuid)

        if status.strip().lower() != 'optimal':
            logger.error("REopt status not optimal. Raising NotOptimal Exception.")
            raise NotOptimal(task=name, run_uuid=self.run_uuid, status=status.strip(), user_uuid=self.user_uuid)

    profiler.profileEnd()
    ModelManager.updateModel('ProfileModel', {name+'_seconds': profiler.getDuration()}, run_uuid)

    # reduce the amount data being transferred between tasks
    if bau:
        del dfm['reopt_inputs_bau']
    else:
        del dfm['reopt_inputs']
    return dfm


def run_decomposed_model(data, model, reopt_inputs,
                         lb_iters=3, max_iters=100):
    time_limit = data["inputs"]["Scenario"]["timeout_seconds"]
    opt_tolerance = data["inputs"]["Scenario"]["optimality_tolerance"]
    reopt_param = julia.Main.Parameter(reopt_inputs)
    lb_models = {}
    ub_models = {}
    for idx in range(1, 13):
        lb_models[idx] = julia.Main.add_decomp_model(model, reopt_param, "lb", idx)
        ub_models[idx] = julia.Main.add_decomp_model(model, reopt_param, "ub", idx)
    lb_result_dicts = build_submodels(lb_models, reopt_param)
    ub_result_dicts = build_submodels(ub_models, reopt_param)
    t_start = time.time()
    lb_result_dicts = solve_subproblems(lb_models, reopt_param, lb_result_dicts, False)
    lb = sum([lb_result_dicts[m]["lower_bound"] for m in range(1, 13)])
    system_sizes = get_average_sizing_decisions(lb_models, reopt_param)
    fix_sizing_decisions(ub_models, reopt_param, system_sizes)
    ub_result_dicts = solve_subproblems(ub_models, reopt_param, ub_result_dicts, False)
    best_result_dicts = copy.deepcopy(ub_result_dicts)
    ub, min_charge_adder, prod_incentives = get_objective_value(ub_result_dicts, reopt_inputs)
    gap = (ub - lb) / lb
    t_elapsed = time.time() - t_start
    for k in range(1,max_iters+1):
        if gap <= opt_tolerance or t_elapsed > time_limit:
            break
        mean_sizes = get_average_sizing_decisions(lb_models, reopt_param)
        if time.time() - t_start > time_limit or gap < opt_tolerance: break
        for i in range(1, 13):
            julia.Main.update_decomp_penalties(lb_models[i], reopt_param, mean_sizes)
        lb_result_dicts = solve_subproblems(lb_models, reopt_param, lb_result_dicts, True)
        iter_lb = sum([lb_result_dicts[m]["lower_bound"] for m in range(1, 13)])
        if iter_lb > lb:
            lb = iter_lb
            gap = (ub - lb) / lb
        if k % lb_iters == 0:
            mean_sizes = get_average_sizing_decisions(lb_models, reopt_param)
            fix_sizing_decisions(ub_models, reopt_param, mean_sizes)
            ub_result_dicts = solve_subproblems(ub_models, reopt_param, ub_result_dicts, True)
            iter_ub, iter_min_charge_adder, iter_prod_incentives = get_objective_value(ub_result_dicts, reopt_inputs)
            if iter_ub < ub:
                ub = iter_ub
                best_result_dicts = copy.deepcopy(ub_result_dicts)
                min_charge_adder = iter_min_charge_adder
                gap = (ub - lb) / lb
        t_elapsed = time.time() - t_start
        k += 1
    results = aggregate_submodel_results(best_result_dicts, ub, min_charge_adder, reopt_inputs["pwf_e"])
    results = julia.Main.convert_to_axis_arrays(reopt_param, results)
    return results


def build_submodels(models, reopt_param):
    result_dicts = {}
    for idx in range(1, 13):
        result_dicts[idx] = julia.Main.reopt_build(models[idx], reopt_param)
    return result_dicts

def solve_subproblems(models, reopt_param, results_dicts, update):
    """
    Solves subproblems, so far in a for loop.
    TODO: make a celery task for each subproblem solve.
    :param models: dictionary in which key=month (1=Jan, 12=Def) and values are JuMP model objects
    :param reopt_param: JuMP parameter object
    :param results_dicts: dictionary in which key=month and vals are submodel results dictionaries
    :param update: Boolean that is True if skipping the creation of output expressions, and False o.w.
    :return: results_dicts -- dictionary in which key=month and vals are submodel results dictionaries
    """
    inputs = []

    for idx in range(1, 13):
        inputs.append({"m": models[idx],
                       "p": reopt_param,
                       "r": results_dicts[idx],
                       "u": update,
                       "month": idx
        })
        solve_subproblem(inputs[idx-1])

    # Note: with task decorator removed, can't call this as a group
    #r = group(solve_subproblem(x) for x in inputs)()
    #r.forget()
    
    results_dicts = {}
    for i in range(1, 13):
        results_dicts[i] = inputs[i-1]["r"]
    return results_dicts


def solve_subproblem(kwargs):
    kwargs["r"] = julia.Main.reopt_solve(kwargs["m"], kwargs["p"], kwargs["r"], kwargs["u"])


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