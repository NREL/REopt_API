from __future__ import absolute_import, unicode_literals
import json
import os
from reo.src.dat_file_manager import DatFileManager
from reo.src.elec_tariff import ElecTariff
from reo.src.load_profile import LoadProfile
from reo.src.site import Site
from reo.src.storage import Storage
from reo.src.techs import PV, Util, Wind
from celery import shared_task


@shared_task(max_retries=5, interval=1)  # could fail to connect to other API's
def setup_scenario(run_uuid, inputs_dict, paths, json_post):
        """

        All error handling is done in validators.py before data is passed to scenario.py
        :param run_uuid:
        :param inputs_dict: validated POST of input parameters
        """
        paths = paths
        run_uuid = run_uuid
        file_post_input = os.path.join(paths['inputs'], "POST.json")
        inputs_dict = inputs_dict
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



            ######################################################################################################
            # everything above this line becomes def build_scenario

            # r = REopt(dfm=dfm, paths=paths, year=inputs_dict['Site']['LoadProfile']['year'])
            #
            # output_dict = r.run(timeout=inputs_dict['timeout_seconds'])
            #
            # output_dict['nested']["Scenario"]["Site"]["LoadProfile"]["year_one_electric_load_series_kw"] = \
            #     lp.unmodified_load_list  # if outage is defined, this is necessary to return the full load profile
            #
            # return output_dict

