import json
import shutil
import os
import traceback
from reo.log_levels import log
from reo.src.dat_file_manager import DatFileManager
from reo.src.elec_tariff import ElecTariff
from reo.src.load_profile import LoadProfile
from reo.src.site import Site
from reo.src.storage import Storage
from reo.src.techs import PV, Util, Wind
from reo.src.reopt import REopt
from utilities import check_directory_created


class Paths(object):
    """
    object for contain project paths. facilitates passing paths to other objects.
    """
    def __init__(self, run_uuid):
        
        self.egg = os.getcwd()
        self.templates = os.path.join(self.egg, "Xpress")
        self.xpress = os.path.join(self.egg, "Xpress")

        self.run = os.path.join(self.xpress, "Run" + str(run_uuid))
        self.files_to_download = os.path.join(self.xpress, "Downloads")

        self.inputs = os.path.join(self.run, "Inputs")
        self.outputs = os.path.join(self.run, "Outputs")
        self.outputs_bau = os.path.join(self.run, "Outputs_bau")
        self.static_outputs = os.path.join(self.egg, "static", "files", str(run_uuid))
        self.utility = os.path.join(self.inputs, "Utility")

        if os.path.exists(self.run):
            shutil.rmtree(self.run)

        for f in [self.run, self.inputs, self.outputs, self.outputs_bau, self.static_outputs, self.utility]:
            os.mkdir(f)
            check_directory_created(f)


class Scenario:

    # if need to debug, change to True, outputs OUT files, GO files, debugging to cmdline
    debug = True

    def __init__(self, run_uuid, inputs_dict):
        """

        All error handling is done in validators.py before data is passed to scenario.py
        :param run_uuid:
        :param inputs_dict: validated POST of input parameters
        """
        self.paths = Paths(run_uuid)
        self.run_uuid = run_uuid
        self.file_post_input = os.path.join(self.paths.inputs, "POST.json")
        self.inputs_dict = inputs_dict
        self.dfm = DatFileManager(run_id=self.run_uuid, paths=self.paths,
                                  n_timesteps=int(inputs_dict['time_steps_per_hour'] * 8760))

    def log_post(self, json_POST):
        with open(self.file_post_input, 'w') as file_post:
            json.dump(json_POST, file_post)

    def run(self):
        try:
            # storage is always made, even if max size is zero (due to REopt's expected inputs)
            storage = Storage(dfm=self.dfm, **self.inputs_dict["Site"]["Storage"])

            site = Site(dfm=self.dfm, **self.inputs_dict["Site"])

            lp = LoadProfile(dfm=self.dfm, user_profile=self.inputs_dict['Site']['LoadProfile'].get('loads_kw'),
                             latitude=self.inputs_dict['Site'].get('latitude'),
                             longitude=self.inputs_dict['Site'].get('longitude'),
                             **self.inputs_dict['Site']['LoadProfile'])

            elec_tariff = ElecTariff(dfm=self.dfm, run_id=self.run_uuid,
                                     load_year=self.inputs_dict['Site']['LoadProfile']['year'],
                                     time_steps_per_hour=self.inputs_dict.get('time_steps_per_hour'),
                                     **self.inputs_dict['Site']['ElectricTariff'])

            if self.inputs_dict["Site"]["PV"]["max_kw"] > 0:
                pv = PV(dfm=self.dfm, latitude=self.inputs_dict['Site'].get('latitude'),
                        longitude=self.inputs_dict['Site'].get('longitude'), **self.inputs_dict["Site"]["PV"])

            if self.inputs_dict["Site"]["Wind"]["max_kw"] > 0:
                wind = Wind(dfm=self.dfm, **self.inputs_dict["Site"]["Wind"])

            util = Util(dfm=self.dfm,
                        outage_start_hour=self.inputs_dict['Site']['LoadProfile'].get("outage_start_hour"),
                        outage_end_hour=self.inputs_dict['Site']['LoadProfile'].get("outage_end_hour"),
                        )

            self.dfm.add_net_metering(
                net_metering_limit=self.inputs_dict['Site']['ElectricTariff'].get("net_metering_limit_kw"),
                interconnection_limit=self.inputs_dict['Site']['ElectricTariff'].get("interconnection_limit_kw")
            )
            self.dfm.finalize()

            r = REopt(dfm=self.dfm, paths=self.paths, year=self.inputs_dict['Site']['LoadProfile']['year'])
            
            output_dict = r.run(timeout=self.inputs_dict['timeout_seconds'])

            output_dict['nested']["Scenario"]["Site"]["LoadProfile"]["year_one_electric_load_series_kw"] = \
                lp.unmodified_load_list  # if outage is defined, this is necessary to return the full load profile
            
            self.cleanup()
            return output_dict

        except Exception as e:
            self.cleanup()
            setattr(e, "traceback", traceback.format_exc())
            raise e

    def cleanup(self):
        # do not call until alternate means of accessing data is developed!
        if not self.debug:
            log("INFO", "Cleaning up folders from: " + self.paths.run)
            shutil.rmtree(self.paths.run)
