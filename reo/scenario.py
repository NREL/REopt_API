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
import traceback
import sys
import os
import logging
log = logging.getLogger(__name__)
from reo.src.data_manager import DataManager
from reo.src.elec_tariff import ElecTariff
from reo.src.load_profile import LoadProfile
from reo.src.fuel_tariff import FuelTariff
from reo.src.load_profile_boiler_fuel import LoadProfileBoilerFuel
from reo.src.load_profile_chiller_electric import LoadProfileChillerElectric
from reo.src.profiler import Profiler
from reo.src.site import Site
from reo.src.storage import Storage, HotTES, ColdTES
from reo.src.techs import PV, Util, Wind, Generator, CHP, Boiler, ElectricChiller, AbsorptionChiller
from celery import shared_task, Task
from reo.models import ModelManager
from reo.exceptions import REoptError, UnexpectedError, LoadProfileError, WindDownloadError, PVWattsDownloadError


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
        if not isinstance(exc, REoptError):
            exc_type, exc_value, exc_traceback = sys.exc_info()
            exc = UnexpectedError(exc_type, exc_value.args[0], exc_traceback, task=self.name, run_uuid=kwargs['run_uuid'],
                              user_uuid=kwargs['data']['inputs']['Scenario'].get('user_uuid'))
        msg = exc.message
        exc.save_to_db()
        self.data["messages"]["error"] = msg
        self.data["outputs"]["Scenario"]["status"] = "An error occurred. See messages for more."
        ModelManager.update_scenario_and_messages(self.data, run_uuid=self.run_uuid)

        self.request.chain = None  # stop the chain?
        self.request.callback = None
        self.request.chord = None  # this seems to stop the infinite chord_unlock call


@shared_task(bind=True, base=ScenarioTask)
def setup_scenario(self, run_uuid, data, raw_post):
    """

    :param run_uuid:
    :param inputs_dict: validated POST of input parameters
    """

    profiler = Profiler()
    inputs_path = os.path.join(os.getcwd(), "input_files")
    self.run_uuid = run_uuid
    self.data = data

    try:
        inputs_dict = data['inputs']['Scenario']
        dfm = DataManager(run_id=run_uuid, n_timesteps=int(inputs_dict['time_steps_per_hour'] * 8760))

        # storage is always made, even if max size is zero (due to REopt's expected inputs)
        storage = Storage(dfm=dfm, **inputs_dict["Site"]["Storage"])

        # Hot TES, always made, same reason as "storage", do unit conversions as needed here
        hot_tes = HotTES(dfm=dfm, **inputs_dict['Site']['HotTES'])

        # Cold TES, always made, same reason as "storage", do unit conversions as needed here
        cold_tes = ColdTES(dfm=dfm, **inputs_dict['Site']['ColdTES'])

        site = Site(dfm=dfm, **inputs_dict["Site"])
        pvs = []

        def setup_pv(pv_dict, latitude, longitude, time_steps_per_hour):
            """
            Create PV object
            :param pv_dict: validated input dictionary for ["Site"]["PV"] (user's POST)
            :return: PV object (from reo.src.techs.py)
            """
            pv = None
            if pv_dict["max_kw"] > 0 or pv_dict["existing_kw"] > 0:
                pv = PV(dfm=dfm, latitude=latitude, longitude=longitude, time_steps_per_hour=time_steps_per_hour,
                        **pv_dict)
                station = pv.station_location
                # update data inputs to reflect the pvwatts station data locations
                # must propagate array_type_to_tilt default assignment back to database
                data['inputs']['Scenario']["Site"]["PV"][pv_dict["pv_number"]-1]["tilt"] = pv.tilt
                tmp = dict()
                tmp['station_latitude'] = station[0]
                tmp['station_longitude'] = station[1]
                tmp['station_distance_km'] = station[2]
                tmp['tilt'] = pv.tilt  # default tilt assigned within techs.py based on array_type
                tmp['azimuth'] = pv.azimuth
                tmp['max_kw'] = pv.max_kw
                tmp['min_kw'] = pv.min_kw
                ModelManager.updateModel('PVModel', tmp, run_uuid, pv_dict["pv_number"])
            return pv

        for pv_dict in inputs_dict["Site"]["PV"]:
            pvs.append(setup_pv(pv_dict, latitude=inputs_dict['Site'].get('latitude'), 
                                longitude=inputs_dict['Site'].get('longitude'), 
                                time_steps_per_hour=inputs_dict['time_steps_per_hour'])
                       )
        
        if inputs_dict["Site"]["Generator"]["generator_only_runs_during_grid_outage"]:
            if inputs_dict['Site']['LoadProfile'].get('outage_start_hour') is not None and inputs_dict['Site']['LoadProfile'].get('outage_end_hour') is not None:

                if inputs_dict["Site"]["Generator"]["max_kw"] > 0 or inputs_dict["Site"]["Generator"]["existing_kw"] > 0:
                    gen = Generator(dfm=dfm, run_uuid=run_uuid,
                            outage_start_hour=inputs_dict['Site']['LoadProfile'].get("outage_start_hour"),
                            outage_end_hour=inputs_dict['Site']['LoadProfile'].get("outage_end_hour"),
                            time_steps_per_hour=inputs_dict.get('time_steps_per_hour'),
                            **inputs_dict["Site"]["Generator"])


        elif not inputs_dict["Site"]["Generator"]["generator_only_runs_during_grid_outage"]:
            if inputs_dict["Site"]["Generator"]["max_kw"] > 0 or inputs_dict["Site"]["Generator"]["existing_kw"] > 0:
                gen = Generator(dfm=dfm, run_uuid=run_uuid,
                            outage_start_hour=inputs_dict['Site']['LoadProfile'].get("outage_start_hour"),
                            outage_end_hour=inputs_dict['Site']['LoadProfile'].get("outage_end_hour"),
                            time_steps_per_hour=inputs_dict.get('time_steps_per_hour'),
                            **inputs_dict["Site"]["Generator"])


        if 'gen' in locals():
            lp = LoadProfile(dfm=dfm,
                             user_profile=inputs_dict['Site']['LoadProfile'].get('loads_kw'),
                             latitude=inputs_dict['Site'].get('latitude'),
                             longitude=inputs_dict['Site'].get('longitude'),
                             pvs=pvs,
                             analysis_years=site.financial.analysis_years,
                             time_steps_per_hour=inputs_dict['time_steps_per_hour'],
                             fuel_avail_before_outage=gen.fuel_avail*gen.fuel_avail_before_outage_pct,
                             gen_existing_kw=gen.existing_kw,
                             gen_min_turn_down=gen.min_turn_down,
                             fuel_slope=gen.fuel_slope,
                             fuel_intercept=gen.fuel_intercept,
                             **inputs_dict['Site']['LoadProfile'])
            tmp = dict()
            tmp['annual_calculated_kwh'] = lp.annual_kwh
            tmp['resilience_check_flag'] = lp.resilience_check_flag
            tmp['sustain_hours'] = lp.sustain_hours
            ModelManager.updateModel('LoadProfileModel', tmp, run_uuid)
        else:
            lp = LoadProfile(dfm=dfm,
                             user_profile=inputs_dict['Site']['LoadProfile'].get('loads_kw'),
                             latitude=inputs_dict['Site'].get('latitude'),
                             longitude=inputs_dict['Site'].get('longitude'),
                             pvs=pvs,
                             analysis_years=site.financial.analysis_years,
                             time_steps_per_hour=inputs_dict['time_steps_per_hour'],
                             fuel_avail_before_outage=0,
                             gen_existing_kw=0,
                             gen_min_turn_down=0,
                             fuel_slope=0,
                             fuel_intercept=0,
                             **inputs_dict['Site']['LoadProfile'])
            tmp = dict()
            tmp['annual_calculated_kwh'] = lp.annual_kwh
            tmp['resilience_check_flag'] = lp.resilience_check_flag
            tmp['sustain_hours'] = lp.sustain_hours
            ModelManager.updateModel('LoadProfileModel', tmp, run_uuid)

        # Checks that the load being sent to optimization does not contatin negative values. We check the loads against
        # a variable tolerance (contingent on PV size since this tech has its existing dispatch added to the loads) and
        # correct loads falling between the threshold and zero.

        #Default tolerance +
        negative_load_tolerance = -0.1 
        # If there is existing PV update the default tolerance based on capacity
        if pvs is not None: 
            existing_pv_kw = 0
            for pv in pvs:
                if getattr(pv,'existing_kw',0) > 0:
                    existing_pv_kw += pv.existing_kw
            
            negative_load_tolerance = min(negative_load_tolerance, existing_pv_kw * -0.005) #kw

        # If values in the load profile fall below the tolerance, raise an exception
        if min(lp.load_list) < negative_load_tolerance:
            message = ("After adding existing generation to the load profile there were still negative electricity "
                       "loads. Loads (non-net) must be equal to or greater than 0.")
            log.error("Scenario.py raising error: " + message)
            lp_error = LoadProfileError(task=self.name, run_uuid=run_uuid, user_uuid=inputs_dict.get('user_uuid'), message=message)
            lp_error.save_to_db()
            raise lp_error
 
        # Correct load profile values that fall between the tolerance and 0
        lp.load_list = [0 if ((x > negative_load_tolerance) and (x < 0)) else x for x in lp.load_list]

        # Load Profile Boiler Fuel
        lpbf = LoadProfileBoilerFuel(dfm=dfm,
            time_steps_per_hour=inputs_dict['time_steps_per_hour'],
            latitude=inputs_dict['Site']['latitude'],
            longitude=inputs_dict['Site']['longitude'],
            nearest_city=lp.nearest_city,
            year=lp.year,
            **inputs_dict['Site']['LoadProfileBoilerFuel']
            )
        # Option 1, retrieve annual load from calculations here and add to database
        tmp = dict()
        tmp['annual_calculated_boiler_fuel_load_mmbtu_bau'] = lpbf.annual_mmbtu
        tmp['year_one_boiler_fuel_load_series_mmbtu_per_hr_bau'] = lpbf.load_list
        ModelManager.updateModel('LoadProfileBoilerFuelModel', tmp, run_uuid)

        # Boiler which supplies the bau boiler fuel load, if there is a boiler fuel load
        if lpbf.annual_mmbtu > 0.0:
            boiler = Boiler(dfm=dfm, **inputs_dict['Site']['Boiler'])
            tmp = dict()
            tmp['boiler_efficiency'] = boiler.boiler_efficiency
            ModelManager.updateModel('BoilerModel', tmp, run_uuid)
        else:
            boiler = None

        # Load Profile Chiller Electric
        lpce = LoadProfileChillerElectric(dfm=dfm, lp=lp,
            time_steps_per_hour=inputs_dict['time_steps_per_hour'],
            latitude=inputs_dict['Site']['latitude'],
            longitude=inputs_dict['Site']['longitude'],
            nearest_city=lp.nearest_city or lpbf.nearest_city,
            year=lp.year,
            **inputs_dict['Site']['LoadProfileChillerElectric']
            )
        # Option 1, retrieve annual load from calculations here and add to database
        tmp = dict()
        tmp['annual_calculated_kwh_bau'] = lpce.annual_kwh
        tmp['year_one_chiller_electric_load_series_kw_bau'] = lpce.load_list
        ModelManager.updateModel('LoadProfileChillerElectricModel', tmp, run_uuid)

        # Electric chiller which supplies the bau electric chiller load, if there is an electric chiller load
        if lpce.annual_kwh > 0.0:
            elecchl = ElectricChiller(dfm=dfm, chiller_electric_series_bau=lpce.load_list,
                                      **inputs_dict['Site']['ElectricChiller'])
            tmp = dict()
            tmp['chiller_cop'] = elecchl.chiller_cop
            tmp['max_kw'] = elecchl.max_kw
            ModelManager.updateModel('ElectricChillerModel', tmp, run_uuid)
        else:
            elecchl = None

        # Absorption chiller
        if inputs_dict["Site"]["AbsorptionChiller"]["max_ton"] > 0:
            absorpchl = AbsorptionChiller(dfm=dfm, **inputs_dict['Site']['AbsorptionChiller'])

        # Fuel tariff
        fuel_tariff = FuelTariff(dfm=dfm, time_steps_per_hour=inputs_dict['time_steps_per_hour'],
                                 **inputs_dict['Site']['FuelTariff'])

        elec_tariff = ElecTariff(dfm=dfm, run_id=run_uuid,
                                 load_year=inputs_dict['Site']['LoadProfile']['year'],
                                 time_steps_per_hour=inputs_dict.get('time_steps_per_hour'),
                                 **inputs_dict['Site']['ElectricTariff'])

        if inputs_dict["Site"]["Wind"]["max_kw"] > 0:
            wind = Wind(dfm=dfm, inputs_path=inputs_path, 
                        latitude=inputs_dict['Site'].get('latitude'),
                        longitude=inputs_dict['Site'].get('longitude'),
                        time_steps_per_hour=inputs_dict.get('time_steps_per_hour'),
                        run_uuid=run_uuid, 
                        **inputs_dict["Site"]["Wind"])

            # must propogate these changes back to database for proforma
            data['inputs']['Scenario']["Site"]["Wind"]["installed_cost_us_dollars_per_kw"] = wind.installed_cost_us_dollars_per_kw
            data['inputs']['Scenario']["Site"]["Wind"]["federal_itc_pct"] = wind.incentives.federal.itc
            tmp = dict()
            tmp['federal_itc_pct'] = wind.incentives.federal.itc
            tmp['installed_cost_us_dollars_per_kw'] = wind.installed_cost_us_dollars_per_kw

            ModelManager.updateModel('WindModel', tmp, run_uuid)
            # TODO: remove the need for this db call by passing these values to process_results.py via reopt.jl


        if inputs_dict["Site"]["CHP"].get("prime_mover") is not None or \
                inputs_dict["Site"]["CHP"].get("max_kw", 0.0) > 0.0:
            if boiler is not None:
                steam_or_hw = boiler.existing_boiler_production_type_steam_or_hw
            else:
                steam_or_hw = 'hot_water'
            chp = CHP(dfm=dfm, run_uuid=run_uuid,
                      existing_boiler_production_type_steam_or_hw=steam_or_hw,
                      oa_temp_degF=inputs_dict['Site']['outdoor_air_temp_degF'],
                      site_elevation_ft=inputs_dict['Site']['elevation_ft'],
                      time_steps_per_hour=inputs_dict.get('time_steps_per_hour'), **inputs_dict['Site']['CHP'])

            # Update the model inputs if there are calculations with the tech class, CHP.py, etc
            #tmp = dict()
            # This is not currently updating anything because tmp is empty (hopefully not doing anything unintended)
            #ModelManager.updateModel('CHPModel', tmp, run_uuid)


        util = Util(dfm=dfm,
                    outage_start_hour=inputs_dict['Site']['LoadProfile'].get("outage_start_hour"),
                    outage_end_hour=inputs_dict['Site']['LoadProfile'].get("outage_end_hour"),
                    )
        dfm.finalize()
        dfm_dict = vars(dfm)  # serialize for celery

        # delete python objects, which are not serializable

        for k in ['storage', 'hot_tes', 'cold_tes', 'site', 'elec_tariff', 'fuel_tariff', 'pvs', 'pvnms',
				'load', 'util', 'heating_load', 'cooling_load'] + dfm.available_techs:
            if dfm_dict.get(k) is not None:
                del dfm_dict[k]

        self.data = data
        profiler.profileEnd()
        tmp = dict()
        tmp['setup_scenario_seconds'] = profiler.getDuration()
        ModelManager.updateModel('ProfileModel', tmp, run_uuid)
        # TODO: remove the need for this db call by passing these values to process_results.py via reopt.jl

        return vars(dfm)  # --> gets passed to REopt runs (BAU and with tech)

    except Exception as e:
        if isinstance(e, LoadProfileError):
            raise e

        if hasattr(e, 'args'):
            if len(e.args) > 0:
                if e.args[0] == 'Wind Dataset Timed Out':
                    raise WindDownloadError(task=self.name, run_uuid=run_uuid, user_uuid=self.data['inputs']['Scenario'].get('user_uuid'))
                if isinstance(e.args[0], str):
                    if e.args[0].startswith('PVWatts'):
                        message = 'PV Watts could not locate a dataset station within the search radius'
                        radius = data['inputs']['Scenario']["Site"]["PV"][0].get("radius") or 0
                        if radius > 0:
                            message += (". A search radius of {} miles was used for the NSRDB dataset (covering the "
                                "continental US, HI and parts of AK). A search radius twice as large ({} miles) was also used "
                                "to query an international dataset. See https://maps.nrel.gov/nsrdb-viewer/ for a map of "
                                "dataset availability or https://nsrdb.nrel.gov/ for dataset documentation.").format(radius, radius*2)
                        else:
                            message += (" from the NSRDB or international datasets. No search threshold was specified when "
                                        "attempting to pull solar resource data from either dataset.")
                        raise PVWattsDownloadError(message=message, task=self.name, run_uuid=run_uuid, user_uuid=self.data['inputs']['Scenario'].get('user_uuid'), traceback=e.args[0])

        exc_type, exc_value, exc_traceback = sys.exc_info()
        log.error("Scenario.py raising error: " + str(exc_value.args[0]))
        raise UnexpectedError(exc_type, exc_value.args[0], traceback.format_tb(exc_traceback), task=self.name, run_uuid=run_uuid,
                              user_uuid=self.data['inputs']['Scenario'].get('user_uuid'))
