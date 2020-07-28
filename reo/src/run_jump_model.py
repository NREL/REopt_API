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
import time
import platform
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

    if platform.system() == "Darwin":
        ext = ".dylib"
    elif platform.system() == "Windows":
        ext = ".dll"
    else:
        ext = ".so"  # if platform.system() == "Linux":
    julia_img_file = os.path.join("julia_envs", "Xpress", "JuliaXpressSysimage" + ext)

    logger.info("Running JuMP model ...")
    try:
        if os.path.isfile(julia_img_file):
            # TODO: clean up this try/except block 
            logger.info("Found Julia image file {}.".format(julia_img_file))
            t_start = time.time()
            api = LibJulia.load()
            api.sysimage = julia_img_file
            api.init_julia()
            from julia import Main
            time_dict["pyjulia_start_seconds"] = time.time() - t_start
        else:
            t_start = time.time()
            j = julia.Julia()
            from julia import Main
            time_dict["pyjulia_start_seconds"] = time.time() - t_start

        t_start = time.time()
        Main.using("Pkg")
        from julia import Pkg
        time_dict["pyjulia_pkg_seconds"] = time.time() - t_start

        if os.environ.get("SOLVER") == "xpress":
            t_start = time.time()
            Pkg.activate("./julia_envs/Xpress/")
            time_dict["pyjulia_activate_seconds"] = time.time() - t_start

            try:
                t_start = time.time()
                Main.include("reo/src/reopt_xpress_model.jl")
                time_dict["pyjulia_include_model_seconds"] = time.time() - t_start

            except ImportError:
                # should only need to instantiate once
                Pkg.instantiate()
                Main.include("reo/src/reopt_xpress_model.jl")

            t_start = time.time()
            model = Main.reopt_model(data["inputs"]["Scenario"]["timeout_seconds"],
                                     data["inputs"]["Scenario"]["optimality_tolerance"])
            time_dict["pyjulia_make_model_seconds"] = time.time() - t_start

        elif os.environ.get("SOLVER") == "cbc":
            t_start = time.time()
            Pkg.activate("./julia_envs/Cbc/")
            time_dict["pyjulia_activate_seconds"] = time.time() - t_start

            t_start = time.time()
            Main.include("reo/src/reopt_cbc_model.jl")
            time_dict["pyjulia_include_model_seconds"] = time.time() - t_start

            t_start = time.time()
            model = Main.reopt_model(float(data["inputs"]["Scenario"]["timeout_seconds"]),
                                     float(data["inputs"]["Scenario"]["optimality_tolerance"]))
            time_dict["pyjulia_make_model_seconds"] = time.time() - t_start

        elif os.environ.get("SOLVER") == "scip":
            t_start = time.time()
            Pkg.activate("./julia_envs/SCIP/")
            time_dict["pyjulia_activate_seconds"] = time.time() - t_start

            t_start = time.time()
            Main.include("reo/src/reopt_scip_model.jl")
            time_dict["pyjulia_include_model_seconds"] = time.time() - t_start

            t_start = time.time()
            model = Main.reopt_model(float(data["inputs"]["Scenario"]["timeout_seconds"]),
                                     float(data["inputs"]["Scenario"]["optimality_tolerance"]))
            time_dict["pyjulia_make_model_seconds"] = time.time() - t_start

        else:
            raise REoptFailedToStartError(
                message="The environment variable SOLVER must be set to one of [xpress, cbc, scip].",
                run_uuid=self.run_uuid, user_uuid=self.user_uuid)

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
                         lb_iters=3, ub_select="peak"):
    time_limit = data["inputs"]["Scenario"]["timeout_seconds"]
    opt_tolerance = data["inputs"]["Scenario"]["optimality_tolerance"]
    reopt_param = julia.Main.Parameter(reopt_inputs)
    print("parameter made.")
    lb_models = {}
    ub_models = {}
    for idx in range(1, 13):
        lb_models[idx] = julia.Main.add_decomp_model(model, reopt_param, "lb", idx)
        ub_models[idx] = julia.Main.add_decomp_model(model, reopt_param, "ub", idx)
    print("models created.")
    lb_result_dicts = build_submodels(lb_models, reopt_param)
    ub_result_dicts = build_submodels(ub_models, reopt_param)
    t_start = time.time()
    lb_result_dicts = solve_subproblems(lb_models, reopt_param, lb_result_dicts, False)
    lb = sum([lb_result_dicts[m]["lower_bound"] for m in range(1, 13)])
    print("lb: ", lb)
    peak_month = julia.Main.get_peak_month(reopt_param)
    print("peak demand month: ", peak_month)
    system_sizes = get_average_sizing_decisions(lb_models, reopt_param)
    print("system sizes obtained.")
    fix_sizing_decisions(ub_models, reopt_param, system_sizes)
    print("system decisions fixed.")
    ub_result_dicts = solve_subproblems(ub_models, reopt_param, ub_result_dicts, False)
    print("ub models solved.")
    ub, min_charge_adder, prod_incentives = get_objective_value(ub_result_dicts, reopt_inputs)
    print("ub: ", ub)
    gap = (ub - lb) / lb
    print("gap: ", gap)
    t_elapsed = time.time() - t_start
    print(gap, opt_tolerance, t_elapsed, time_limit)
    k = 1
    while gap > opt_tolerance and t_elapsed < time_limit:
        mean_sizes = get_average_sizing_decisions(lb_models, reopt_param)
        print(mean_sizes)
        if time.time() - t_start > time_limit or gap < opt_tolerance: break
        print("iter ", k)
        print([lb_result_dicts[m]["chp_kw"] for m in range(1,13)])
        for i in range(1, 13):
            julia.Main.update_decomp_penalties(lb_models[i], reopt_param, mean_sizes)
        lb_result_dicts = solve_subproblems(lb_models, reopt_param, lb_result_dicts, True)
        iter_lb = sum([lb_result_dicts[m]["lower_bound"] for m in range(1, 13)])
        print("new lb", iter_lb)
        if iter_lb > lb:
            lb = iter_lb
            gap = (ub - lb) / lb
            print("new lb, new gap: ", gap)
        if k % lb_iters == 0:
            mean_sizes = get_average_sizing_decisions(lb_models, reopt_param)

            fix_sizing_decisions(ub_models, reopt_param, mean_sizes)
            ub_result_dicts = solve_subproblems(ub_models, reopt_param, ub_result_dicts, True)
            iter_ub, iter_min_charge_adder, iter_prod_incentives = get_objective_value(ub_result_dicts, reopt_inputs)
            print("iter_ub: ", iter_ub)
            if iter_ub < ub:
                ub = iter_ub
                best_result_dicts = copy.deepcopy()
                min_charge_adder = iter_min_charge_adder
                prod_incentives = iter_prod_incentives
                gap = (ub - lb) / lb
                print("new ub, gap: ", gap)
        t_elapsed = time.time() - t_start
        k += 1
    print("final gap: ", gap)
    results = aggregate_submodel_results(ub_result_dicts, ub, min_charge_adder, reopt_inputs["pwf_e"])
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
    jobs = group(solve_subproblem.s(x) for x in inputs)
    r = jobs.apply()
    results = r.get()
    for i, result in enumerate(results):
        results_dicts[i+1] = result
    return results_dicts


@shared_task(name='solve_subproblem')
def solve_subproblem(kwargs):
    return julia.Main.reopt_solve(kwargs["m"], kwargs["p"], kwargs["r"], kwargs["u"])


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
    if len(reopt_inputs['DemandLookbackMonths']) > 0:
        obj += get_added_peak_tou_costs(ub_result_dicts, reopt_inputs)
    return obj, min_charge_adder, prod_incentives

def get_added_peak_tou_costs(ub_result_dicts, reopt_inputs):
    """
    Calculated added TOU costs to according to peak lookback months.
    :param ub_result_dicts:
    :param reopt_inputs:
    :return:
    """
    if (reopt_inputs['DemandLookbackPercent'] == 0.0
            or len(reopt_inputs['DemandLookbackMonths']) == 0
            or len(reopt_inputs['Ratchets']) == 0
    ):
        return 0.0

    """
    
    """

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