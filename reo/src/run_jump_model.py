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
from celery import shared_task, Task
from reo.exceptions import REoptError, OptimizationTimeout, UnexpectedError, NotOptimal, REoptFailedToStartError
from reo.models import ModelManager
from reo.src.profiler import Profiler
from celery.utils.log import get_task_logger
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
    self.profiler = Profiler()
    name = 'reopt' if not bau else 'reopt_bau'
    reopt_inputs = dfm['reopt_inputs'] if not bau else dfm['reopt_inputs_bau']
    self.data = data
    self.run_uuid = data['outputs']['Scenario']['run_uuid']
    self.user_uuid = data['outputs']['Scenario'].get('user_uuid')

    logger.info("Running JuMP model ...")
    try:
        j = julia.Julia()
        j.using("Pkg")
        if os.environ.get("SOLVER") == "xpress":
            j.eval('Pkg.activate("./julia_envs/Xpress/")')
            try:
                j.include("reo/src/reopt_xpress_model.jl")
            except ImportError:
                # should only need to instantiate once
                j.eval('Pkg.instantiate()')
                j.include("reo/src/reopt_xpress_model.jl")
            model = j.reopt_model(data["inputs"]["Scenario"]["timeout_seconds"])
        elif os.environ.get("SOLVER") == "cbc":
            j.eval('Pkg.activate("./julia_envs/Cbc/")')
            j.include("reo/src/reopt_cbc_model.jl")
            model = j.reopt_model(float(data["inputs"]["Scenario"]["timeout_seconds"]))
        elif os.environ.get("SOLVER") == "scip":
            j.eval('Pkg.activate("./julia_envs/SCIP/")')
            j.include("reo/src/reopt_scip_model.jl")
            model = j.reopt_model(float(data["inputs"]["Scenario"]["timeout_seconds"]))
        else:
            raise REoptFailedToStartError(
                message="The environment variable SOLVER must be set to one of [xpress, cbc, scip].",
                run_uuid=self.run_uuid, user_uuid=self.user_uuid)

        j.include("reo/src/reopt.jl")
        results = j.reopt(model, data, reopt_inputs)
    except Exception as e:
        if isinstance(e, REoptFailedToStartError):
            raise e
        exc_type, exc_value, exc_traceback = sys.exc_info()
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

    self.profiler.profileEnd()
    tmp = dict()
    tmp[name+'_seconds'] = self.profiler.getDuration()
    ModelManager.updateModel('ProfileModel', tmp, run_uuid)

    # reduce the amount data being transferred between tasks
    if bau:
        del dfm['reopt_inputs_bau']
    else:
        del dfm['reopt_inputs']
    return dfm
