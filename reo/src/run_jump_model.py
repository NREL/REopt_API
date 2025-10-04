# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
import sys
import traceback
import os
import time
import requests
from celery import shared_task, Task
from reo.exceptions import REoptError, OptimizationTimeout, UnexpectedError, NotOptimal, REoptFailedToStartError
from reo.models import ModelManager
from reo.src.profiler import Profiler
from celery.utils.log import get_task_logger
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


@shared_task(base=RunJumpModelTask)
def run_jump_model(dfm, data, bau=False):
    profiler = Profiler()
    time_dict = dict()
    name = 'reopt' if not bau else 'reopt_bau'
    reopt_inputs = dfm['reopt_inputs'] if not bau else dfm['reopt_inputs_bau']
    run_uuid = data['outputs']['Scenario']['run_uuid']
    user_uuid = data['outputs']['Scenario'].get('user_uuid')
    reopt_inputs["timeout_seconds"] = data['inputs']['Scenario']['timeout_seconds']
    reopt_inputs["tolerance"] = data['inputs']['Scenario']['optimality_tolerance_bau'] if bau \
        else data['inputs']['Scenario']['optimality_tolerance_techs']

    logger.info("Running {} JuMP model ...".format("BAU" if bau else ""))
    try:
        t_start = time.time()
        julia_host = os.environ.get('JULIA_HOST', "julia")
        response = requests.post("http://" + julia_host + ":8081/job/", json=reopt_inputs)
        results = response.json()
        if response.status_code == 500:
            raise REoptFailedToStartError(task=name, message=results["error"], run_uuid=run_uuid, user_uuid=user_uuid)
        time_dict["pyjulia_run_reopt_seconds"] = time.time() - t_start
        results.update(time_dict)

    except Exception as e:
        if isinstance(e, REoptFailedToStartError):
            raise e
        elif "DimensionMismatch" in str(e.args[0]):  # JuMP may mishandle a timeout when no feasible solution is returned
            msg = "Optimization exceeded timeout: {} seconds.".format(data["inputs"]["Scenario"]["timeout_seconds"])
            logger.info(msg)
            raise OptimizationTimeout(task=name, message=msg, run_uuid=run_uuid, user_uuid=user_uuid)
        elif "RemoteDisconnected" in str(e.args[0]):
            msg = "The Julia API disconnected."
            logger.error(msg)
            raise REoptFailedToStartError(task=name, message=msg, run_uuid=run_uuid, user_uuid=user_uuid)

        # ADD JULIA EXCEPTION HERE
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error("REopt.py raise unexpected error: UUID: " + str(run_uuid))
        raise UnexpectedError(exc_type, exc_value, traceback.format_tb(exc_traceback), task=name, run_uuid=run_uuid, user_uuid=user_uuid)
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
            raise OptimizationTimeout(task=name, message=msg, run_uuid=run_uuid, user_uuid=user_uuid)
        elif status.strip().lower() != 'optimal':
            logger.error("{} REopt status not optimal ({}). Raising NotOptimal Exception.".format(
                "BAU" if bau else "", status.strip())
            )
            raise NotOptimal(task=name, run_uuid=run_uuid, status=status.strip(), user_uuid=user_uuid)

    profiler.profileEnd()
    ModelManager.updateModel('ProfileModel', {name+'_seconds': profiler.getDuration()}, run_uuid)

    # reduce the amount data being transferred between tasks
    if bau:
        del dfm['reopt_inputs_bau']
    else:
        del dfm['reopt_inputs']
    return dfm
