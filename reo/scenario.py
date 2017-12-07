from __future__ import absolute_import, unicode_literals
import json
import os
import sys
from reo.src.dat_file_manager import DatFileManager
from reo.src.elec_tariff import ElecTariff
from reo.src.load_profile import LoadProfile
from reo.src.site import Site
from reo.src.storage import Storage
from reo.src.techs import PV, Util, Wind
from celery import shared_task, Task
from reo.models import ModelManager
from reo.exceptions import REoptError, UnexpectedError
from reo.log_levels import log


class ScenarioTask(Task):
    """
    Used to define custom Error handling for celery task
    """

    name = 'scenario'
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
        if isinstance(exc, REoptError):
            exc.save_to_db()

        self.data["messages"]["errors"] = exc.message
        self.data["outputs"]["Scenario"]["status"] = "An error occurred. See messages for more."
        ModelManager.update_scenario_and_messages(self.data, run_uuid=self.run_uuid)

        # self.request.chain = None  # stop the chain?
        # self.request.callback = None
        self.request.chord = None  # this seems to stop the infinite chord_unlock call


@shared_task(bind=True, base=ScenarioTask)
def setup_scenario(self, run_uuid, paths, json_post, data):
    """

    All error handling is done in validators.py before data is passed to scenario.py
    :param run_uuid:
    :param inputs_dict: validated POST of input parameters
    """
    self.run_uuid = run_uuid
    self.data = data
    try:
        file_post_input = os.path.join(paths['inputs'], "POST.json")
        inputs_dict = data['inputs']['Scenario']
        dfm = DatFileManager(run_id=run_uuid, paths=paths,
                             n_timesteps=int(inputs_dict['time_steps_per_hour'] * 8760))

        with open(file_post_input, 'w') as file_post:
            json.dump(json_post, file_post)

        # storage is always made, even if max size is zero (due to REopt's expected inputs)
        storage = Storage(dfm=dfm, **inputs_dict["Site"]["Storage"])

        site = Site(dfm=dfm, **inputs_dict["Site"])

        lp = LoadProfile(dfm=dfm, user_profile=inputs_dict['Site']['LoadProfile'].get('loads_kw'),
                         latitude=inputs_dict['Site'].get('latitude'),
                         longitude=inputs_dict['Site'].get('longitude'),
                         **inputs_dict['Site']['LoadProfile'])

        elec_tariff = ElecTariff(dfm=dfm, run_id=run_uuid,
                                 load_year=inputs_dict['Site']['LoadProfile']['year'],
                                 time_steps_per_hour=inputs_dict.get('time_steps_per_hour'),
                                 **inputs_dict['Site']['ElectricTariff'])

        if inputs_dict["Site"]["PV"]["max_kw"] > 0:
            pv = PV(dfm=dfm, latitude=inputs_dict['Site'].get('latitude'),
                    longitude=inputs_dict['Site'].get('longitude'), **inputs_dict["Site"]["PV"])

        if inputs_dict["Site"]["Wind"]["max_kw"] > 0:
            wind = Wind(dfm=dfm, **inputs_dict["Site"]["Wind"])

        util = Util(dfm=dfm,
                    outage_start_hour=inputs_dict['Site']['LoadProfile'].get("outage_start_hour"),
                    outage_end_hour=inputs_dict['Site']['LoadProfile'].get("outage_end_hour"),
                    )

        dfm.add_net_metering(
            net_metering_limit=inputs_dict['Site']['ElectricTariff'].get("net_metering_limit_kw"),
            interconnection_limit=inputs_dict['Site']['ElectricTariff'].get("interconnection_limit_kw")
        )
        dfm.finalize()
        dfm_dict = vars(dfm)  # serialize for celery
        for k in ['storage', 'pv', 'wind', 'site', 'elec_tariff', 'util', 'pvnm', 'windnm']:
            if dfm_dict.get(k) is not None:
                del dfm_dict[k]
        return vars(dfm)  # --> REopt runs (BAU and with tech)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        log("UnexpectedError", "{} occured in reo.results.parse_run_outputs.".format(exc_type))
        raise UnexpectedError(exc_type, exc_value, exc_traceback, task=self.name, run_uuid=run_uuid)
