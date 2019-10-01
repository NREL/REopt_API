from __future__ import absolute_import, unicode_literals
import json
import os
import sys
from reo.log_levels import log
from reo.src.dat_file_manager import DatFileManager
from reo.src.elec_tariff import ElecTariff
from reo.src.load_profile import LoadProfile
from reo.src.profiler import Profiler
from reo.src.site import Site
from reo.src.storage import Storage
from reo.src.techs import PV, Util, Wind, Generator
from celery import shared_task, Task
from reo.models import ModelManager
from reo.exceptions import REoptError, UnexpectedError, LoadProfileError, WindDownloadError
from reo.src.paths import Paths


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

        self.data["messages"]["error"] = exc.message
        self.data["outputs"]["Scenario"]["status"] = "An error occurred. See messages for more."
        ModelManager.update_scenario_and_messages(self.data, run_uuid=self.run_uuid)

        # self.request.chain = None  # stop the chain?
        # self.request.callback = None
        self.request.chord = None  # this seems to stop the infinite chord_unlock call


@shared_task(bind=True, base=ScenarioTask)
def setup_scenario(self, run_uuid, data, raw_post):
    """

    :param run_uuid:
    :param inputs_dict: validated POST of input parameters
    """

    self.profiler = Profiler()
    paths = vars(Paths(run_uuid=run_uuid))
    self.run_uuid = run_uuid
    self.data = data

    # Log POST request
    file_post_input = os.path.join(paths['inputs'], "POST.json")
    with open(file_post_input, 'w') as file_post:
        json.dump(raw_post, file_post)

    try:
        inputs_dict = data['inputs']['Scenario']
        dfm = DatFileManager(run_id=run_uuid, paths=paths,
                             n_timesteps=int(inputs_dict['time_steps_per_hour'] * 8760))

        # storage is always made, even if max size is zero (due to REopt's expected inputs)
        storage = Storage(dfm=dfm, **inputs_dict["Site"]["Storage"])

        site = Site(dfm=dfm, **inputs_dict["Site"])

        if inputs_dict["Site"]["PV"]["max_kw"] > 0 or inputs_dict["Site"]["PV"]["existing_kw"] > 0:
            pv = PV(dfm=dfm, latitude=inputs_dict['Site'].get('latitude'),
                    longitude=inputs_dict['Site'].get('longitude'), time_steps_per_hour=inputs_dict['time_steps_per_hour'],
                    **inputs_dict["Site"]["PV"])
            station = pv.station_location

            # update data inputs to reflect the pvwatts station data locations
            # must propagate array_type_to_tilt default assignment back to database
            data['inputs']['Scenario']["Site"]["PV"]["tilt"] = pv.tilt
            tmp = dict()
            tmp['station_latitude'] = station[0]
            tmp['station_longitude'] = station[1]
            tmp['station_distance_km'] =station[2]
            tmp['tilt'] = pv.tilt                  #default tilt assigned within techs.py based on array_type
            tmp['max_kw'] = pv.max_kw
            tmp['min_kw'] = pv.min_kw
            ModelManager.updateModel('PVModel', tmp, run_uuid)


        else:
            pv = None


        if inputs_dict["Site"]["Generator"]["max_kw"] > 0 or inputs_dict["Site"]["Generator"]["existing_kw"] > 0:
            gen = Generator(dfm=dfm, run_uuid=run_uuid,
                            outage_start_hour=inputs_dict['Site']['LoadProfile'].get("outage_start_hour"),
                            outage_end_hour=inputs_dict['Site']['LoadProfile'].get("outage_end_hour"),
                            time_steps_per_hour=inputs_dict.get('time_steps_per_hour'),
                            **inputs_dict["Site"]["Generator"])

            tmp = dict()
            tmp['fuel_slope_gal_per_kwh'] = gen.fuel_slope
            tmp['fuel_intercept_gal_per_hr'] = gen.fuel_intercept
            tmp['max_kw'] = gen.max_kw
            tmp['min_kw'] = gen.min_kw
            ModelManager.updateModel('GeneratorModel', tmp, run_uuid)

        try:
            if 'gen' in locals():
                lp = LoadProfile(dfm=dfm,
                                 user_profile=inputs_dict['Site']['LoadProfile'].get('loads_kw'),
                                 latitude=inputs_dict['Site'].get('latitude'),
                                 longitude=inputs_dict['Site'].get('longitude'),
                                 pv=pv,
                                 analysis_years=site.financial.analysis_years,
                                 time_steps_per_hour=inputs_dict['time_steps_per_hour'],
                                 fuel_avail_before_outage=gen.fuel_avail*gen.fuel_avail_before_outage_pct,
                                 gen_existing_kw=gen.existing_kw,
                                 gen_min_turn_down=gen.min_turn_down,
                                 fuel_slope=gen.fuel_slope,
                                 fuel_intercept=gen.fuel_intercept,
                                 **inputs_dict['Site']['LoadProfile'])
                tmp = dict()
                tmp['resilience_check_flag'] = lp.resilience_check_flag
                tmp['sustain_hours'] = lp.sustain_hours
                ModelManager.updateModel('LoadProfileModel', tmp, run_uuid)
            else:
                lp = LoadProfile(dfm=dfm,
                                 user_profile=inputs_dict['Site']['LoadProfile'].get('loads_kw'),
                                 latitude=inputs_dict['Site'].get('latitude'),
                                 longitude=inputs_dict['Site'].get('longitude'),
                                 pv=pv,
                                 analysis_years=site.financial.analysis_years,
                                 time_steps_per_hour=inputs_dict['time_steps_per_hour'],
                                 fuel_avail_before_outage=0,
                                 gen_existing_kw=0,
                                 gen_min_turn_down=0,
                                 fuel_slope=0,
                                 fuel_intercept=0,
                                 **inputs_dict['Site']['LoadProfile'])
                tmp = dict()
                tmp['resilience_check_flag'] = lp.resilience_check_flag
                tmp['sustain_hours'] = lp.sustain_hours
                ModelManager.updateModel('LoadProfileModel', tmp, run_uuid)

        except Exception as lp_error:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            log.error("Scenario.py raising error: " + exc_value.message)
            lp_error = LoadProfileError(exc_value.message, exc_traceback, self.name, run_uuid, user_uuid=inputs_dict.get('user_uuid'))
            lp_error.save_to_db()
            raise lp_error

        elec_tariff = ElecTariff(dfm=dfm, run_id=run_uuid,
                                 load_year=inputs_dict['Site']['LoadProfile']['year'],
                                 time_steps_per_hour=inputs_dict.get('time_steps_per_hour'),
                                 **inputs_dict['Site']['ElectricTariff'])

        if inputs_dict["Site"]["Wind"]["max_kw"] > 0:
            wind = Wind(dfm=dfm, latitude=inputs_dict['Site'].get('latitude'),
                        longitude=inputs_dict['Site'].get('longitude'),time_steps_per_hour=inputs_dict.get('time_steps_per_hour'), run_uuid=run_uuid, **inputs_dict["Site"]["Wind"])

            # must propogate these changes back to database for proforma
            data['inputs']['Scenario']["Site"]["Wind"]["installed_cost_us_dollars_per_kw"] = wind.installed_cost_us_dollars_per_kw
            data['inputs']['Scenario']["Site"]["Wind"]["federal_itc_pct"] = wind.incentives.federal.itc
            tmp = dict()
            tmp['federal_itc_pct'] = wind.incentives.federal.itc
            tmp['installed_cost_us_dollars_per_kw'] = wind.installed_cost_us_dollars_per_kw

            ModelManager.updateModel('WindModel', tmp, run_uuid)

        
        if inputs_dict["Site"]["Generator"]["max_kw"] > 0 or inputs_dict["Site"]["Generator"]["existing_kw"] > 0:
            gen = Generator(dfm=dfm, run_uuid=run_uuid,
                            outage_start_hour=inputs_dict['Site']['LoadProfile'].get("outage_start_hour"),
                            outage_end_hour=inputs_dict['Site']['LoadProfile'].get("outage_end_hour"),
                            time_steps_per_hour=inputs_dict.get('time_steps_per_hour'),**inputs_dict["Site"]["Generator"]
                            )

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
            # delete python objects, which are not serializable
        for k in ['storage', 'pv', 'wind', 'site', 'elec_tariff', 'util', 'pvnm', 'windnm', 'generator']:
            if dfm_dict.get(k) is not None:
                del dfm_dict[k]

        self.data = data
        self.profiler.profileEnd()
        tmp = dict()
        tmp['setup_scenario_seconds'] = self.profiler.getDuration()
        ModelManager.updateModel('ProfileModel', tmp, run_uuid)

        return vars(dfm)  # --> gets passed to REopt runs (BAU and with tech)

    except Exception as e:
        if isinstance(e, LoadProfileError):
                raise e
        
        elif hasattr(e, 'message'):
            if e.message == 'Wind Dataset Timed Out':
                raise WindDownloadError(task=self.name, run_uuid=run_uuid,user_uuid=self.data['inputs']['Scenario'].get('user_uuid'))
            else:
                log.error(e.message)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                raise UnexpectedError(exc_type, exc_value, exc_traceback, task=self.name, run_uuid=run_uuid, message=e.message,user_uuid=self.data['inputs']['Scenario'].get('user_uuid'))

        elif isinstance(e, REoptError):
            pass
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if hasattr(exc_value, 'name'):
                if exc_value.name == 'LoadProfileError':
                    log.error("Scenario.py raising error: " + exc_value.message)
                    pass
            else:
                log.error("Scenario.py raising error: " + exc_value)
                raise UnexpectedError(exc_type, exc_value, exc_traceback, task=self.name, run_uuid=run_uuid,user_uuid=self.data['inputs']['Scenario'].get('user_uuid'))
