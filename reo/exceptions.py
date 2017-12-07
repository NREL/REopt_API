from reo.models import ErrorModel
from reo.log_levels import log
from reo.models import ModelManager
from celery import Task


class REoptError(Exception):
    """
    Base class for exceptions in reo app.
    call to super().__init__ will save ErrorModel to database.

    """

    def __init__(self, task='', name='', run_uuid='', message='', traceback=''):
        """

        :param task: task where error occurred, e.g. scenario_setup, reopt, process_results
        :param name: name of error class, e.g. SubprocessTimeout
        :param run_uuid:
        :param message: message that is sent back to user in messages: errors
        :param traceback: sys.exc_info()[2]
        """
        msg_with_email = " Please email reopt@nrel.gov with your run_uuid ({}) for support.".format(run_uuid)
        self.message = message + msg_with_email  # msg_with_email included in messages: error response, but not in error table
        self.task = task
        self.run_uuid = run_uuid
        self.traceback = traceback
        self.name = name

    def save_to_db(self):
        """
        ErrorModel(django.db.models.Model)
            task = models.TextField(blank=True, default='')
            name = models.TextField(blank=True, default='')
            run_uuid = models.TextField(blank=True, default='')
            message = models.TextField(blank=True, default='')
            traceback = models.TextField(blank=True, default='')
        """
        em = ErrorModel(task=self.task, name=self.name, run_uuid=self.run_uuid, message=self.message,
                        traceback=self.traceback)
        em.save()


class SubprocessTimeout(REoptError):
    """
    Exception raised when a subprocess times out

    """
    __name__ = 'SubprocessTimeout'

    def __init__(self, task='reopt', run_uuid='', message='', traceback=''):
        """

        :param task: task where error occurred
        :param run_uuid:
        :param message: message that is sent back to user in messages: errors
        :param traceback: saved to database for debugging
        """
        super(SubprocessTimeout, self).__init__(task, self.__name__, run_uuid, message, traceback)


class NotOptimal(REoptError):
    """
    Exception raised when a subprocess times out

    """
    __name__ = 'NotOptimal'

    def __init__(self, task='reopt', run_uuid='', traceback='', status=''):
        """

        :param task: task where error occurred
        :param run_uuid:
        :param traceback: saved to database for debugging
        """
        log("INFO", "WHAT?!?!?!")
        msg = "REopt could not find an optimal solution for these inputs."
        if status == 'infeasible':
            msg += " The problem is likely due to constraints that make a solution infeasible, " \
                   + "such as a grid outage without enough resources to meet the load during the outage."
        super(NotOptimal, self).__init__(task, self.__name__, run_uuid, message=msg, traceback="status: " + status)


class UnexpectedException(REoptError):
    """
    REopt catch-all exception class

    Attributes:
        message - explanation of the error
    """

    def __init__(self, exc_type, exc_value, exc_traceback):

        self.exc_type = exc_type
        self.exc_value = exc_value
        self.exc_traceback = exc_traceback


class TaskExceptionHandler(Task):

    max_retries = 0

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        log a bunch of stuff for debugging
        save message: error and outputs: Scenario: status
        need to stop rest of chain!?
        :param exc: The exception raised by the task.
        :param task_id: Unique id of the failed task. (not the run_uuid)
        :param args: Original arguments for the task that failed.
        :param kwargs: Original keyword arguments for the task that failed.
        :param einfo: ExceptionInfo instance, containing the traceback.

        :return: None, The return value of this handler is ignored.
        """
        exc.save_to_db()
        data = kwargs['data']
        data["messages"]["errors"] = exc.message
        data["outputs"]["Scenario"]["status"] = "An error occurred. See messages for more."
        ModelManager.update_scenario_and_messages(data, run_uuid=data['outputs']['Scenario']['run_uuid'])

        # self.request.chain = None  # stop the chain?
        # self.request.callback = None
        self.request.chord = None  # this seems to stop the infinite chord_unlock call