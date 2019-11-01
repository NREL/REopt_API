import julia
from celery import shared_task, Task
from reo.exceptions import REoptError, SubprocessTimeout, UnexpectedError, NotOptimal, REoptFailedToStartError
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
        data = kwargs['data']
        data["messages"]["error"] = exc.message
        data["outputs"]["Scenario"]["status"] = "An error occurred. See messages for more."
        ModelManager.update_scenario_and_messages(data, run_uuid=data['outputs']['Scenario']['run_uuid'])

        self.request.chain = None  # stop the chain
        self.request.callback = None
        self.request.chord = None  # this seems to stop the infinite chord_unlock call


@shared_task(bind=True, base=RunJumpModelTask)
def run_jump_model(self, dfm_list, data, run_uuid, bau=False):
    # TODO: dfm_list will become just dfm (and should rename dfm since no longer using dat files)
    dfm = dfm_list[0]
    self.profiler = Profiler()
    name = 'reopt' if not bau else 'reopt_bau'
    reopt_inputs = dfm['reopt_inputs'] if not bau else dfm['reopt_inputs_bau']
    self.data = data
    self.run_uuid = data['outputs']['Scenario']['run_uuid']
    self.user_uuid = data['outputs']['Scenario'].get('user_uuid')

    logger.info("Running JuMP model ...")
    try:
        j = julia.Julia()
        j.include("reo/src/reopt.jl")
        results = j.reopt(data, **reopt_inputs)
    except Exception as e:
        # TODO: exception handling
        raise e
    else:
        status = results["outputs"]["Scenario"]["status"]
        logger.info("REopt run successful. Status {}".format(status))
        dfm['results'] = results  # will be flat dict

        if status.strip().lower() != 'optimal':
            logger.error("REopt status not optimal. Raising NotOptimal Exception.")
            raise NotOptimal(task=name, run_uuid=self.run_uuid, status=status.strip(), user_uuid=self.user_uuid)

    self.profiler.profileEnd()
    tmp = dict()
    tmp[name+'_seconds'] = self.profiler.getDuration()
    ModelManager.updateModel('ProfileModel', tmp, run_uuid)

    return dfm
