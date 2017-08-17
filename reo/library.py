# python libraries
# some libraries are being imported via the 'import *' statements below
# including at least 'os' and 'json'
import json
import shutil

from api_definitions import *
from reo.src.dat_file_manager import DatFileManager
from reo.src.elec_tariff import ElecTariff
from reo.src.load_profile import LoadProfile
from reo.src.site import Site
from reo.src.storage import Storage
from reo.src.techs import PV, Util
from reo.src.urdb_parse import *
from results import Results
from utilities import Command, check_directory_created, is_error


class Paths(object):
    """
    object for contain project paths. facilitates passing paths to other objects.
    """
    def __init__(self, run_uuid, run_input_id):
        
        self.egg = os.getcwd()
        self.templates = os.path.join(self.egg, "Xpress")
        self.xpress = os.path.join(self.egg, "Xpress")

        self.run = os.path.join(self.xpress, "Run" + str(run_input_id))
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


class DatLibrary:
    """
    Instantiated in models.py within RunInput.create_output,
    which in turn is called by RunInputResource.obj_create in api.py
    """

    # if need to debug, change to True, outputs OUT files, GO files, debugging to cmdline
    debug = True
    xpress_model = "REopt_API.mos"
    time_steps_per_hour = 1

    def inputs(self, **args):
        return inputs(**args)

    def outputs(self, **args):
        return outputs(**args)

    def __init__(self, run_uuid, run_input_id, inputs_dict):
        """

        All error handling is done in validators.py before data is passed to library.py
        :param run_uuid:
        :param run_input_id:
        :param inputs_dict: dictionary of API key, value pairs. Any value that is in api_definitions' inputs
        that is not included in the inputs_dict is added to the inputs_dict with the default api_definitions value.
        """
        self.paths = Paths(run_uuid, run_input_id)
        self.timed_out = False  # is this used?
        self.net_metering = False

        # Command line constants
        self.command_line_constants = list()
        self.command_line_constants.append("ScenarioNum=" + str(run_input_id))

        # calculated values
        self.run_input_id = run_input_id

        self.file_output = os.path.join(self.paths.outputs, "REopt_results.json")
        self.file_post_input = os.path.join(self.paths.inputs, "POST.json")
        self.file_cmd_input = os.path.join(self.paths.inputs, "cmd.log")
        self.file_cmd_input_bau = os.path.join(self.paths.inputs, "cmd_bau.log")

        for k, v in self.inputs(full_list=True).items():
            # see api_definitions.py for attributes set here
            if k == 'load_profile_name' and inputs_dict.get(k) is not None:
                setattr(self, k, inputs_dict.get(k).replace(" ", ""))

            elif inputs_dict.get(k) is None:
                setattr(self, k, self.inputs()[k].get('default'))

            else:
                setattr(self, k, inputs_dict.get(k))

        if self.tilt is None:
            self.tilt = self.latitude

        for k in self.outputs():
            setattr(self, k, None)

        self.update_types()

        for k, v in inputs(full_list=True).iteritems():
            inputs_dict.setdefault(k, v['default'])
        self.inputs_dict = inputs_dict

        self.dfm = DatFileManager(run_id=self.run_input_id, paths=self.paths,
                                  n_timesteps=inputs_dict['time_steps_per_hour'] * 8760)

    def log_post(self, json_POST):
        with open(self.file_post_input, 'w') as file_post:
            json.dump(json_POST, file_post)

    def get_path_run(self):
        return self.paths.run

    def get_path_run_inputs(self):
        return self.paths.inputs

    def get_path_run_outputs(self):
        return self.paths.outputs

    def get_path_run_outputs_bau(self):
        return self.paths.outputs_bau

    def update_types(self):
        for group in [self.inputs(full_list=True), self.outputs()]:
            for k, v in group.items():
                value = getattr(self, k)

                if value is not None:
                    if v['type'] == float:
                        if v['pct']:
                            if value > 1.0:
                                setattr(self, k, float(value) * 0.01)

                    elif v['type'] == list:
                        if 'listtype' in v:
                            if v['listtype'] != str:
                                value = [float(i) for i in getattr(self, k)]
                                setattr(self, k, value)
                    else:
                        setattr(self, k, v['type'](value))

    def get_subtask_inputs(self, name):
        output = {}
        defaults = self.inputs(filter=name)

        for k in defaults.keys():
            output[k] = getattr(self, k)
            if output[k] is None:
                default = defaults[k].get('default')
                if default is not None:
                    output[k] = default

        return output

    def run(self):

        output_dict = dict()

        storage = Storage(
            min_kw=self.batt_kw_min,
            max_kw=self.batt_kw_max,
            min_kwh=self.batt_kwh_min,
            max_kwh=self.batt_kwh_max,
            efficiency=self.batt_efficiency,
            inverter_efficiency=self.batt_inverter_efficiency,
            rectifier_efficiency=self.batt_rectifier_efficiency,
            soc_min=self.batt_soc_min,
            soc_init=self.batt_soc_init,
            can_grid_charge=self.batt_can_gridcharge,
            us_dollar_per_kw=self.batt_cost_kw,
            us_dollar_per_kwh=self.batt_cost_kwh,
            replace_us_dollar_per_kw=self.batt_replacement_cost_kw,
            replace_us_dollar_per_kwh=self.batt_replacement_cost_kwh,
            replace_kw_years=self.batt_replacement_year_kw,
            replace_kwh_years=self.batt_replacement_year_kwh,
            **self.inputs_dict
        )

        site = Site(**self.inputs_dict)
        # following 2 lines are necessary for returning *some* of the assigned values.
        # at least owner_tax_rate and owner_discount_rate are necessary for proforma (because they come in as Nones
        # and then we assign them to the off_taker values to represent single party model)
        for k in site.financials.__dict__.keys():
            setattr(self, k, getattr(site.financials, k))

        self.create_loads()
        self.create_utility()

        pv = PV(**self.inputs_dict)
        # following 2 lines are necessary for returning the assigned values
        self.pv_degradation_rate = pv.degradation_rate
        self.pv_kw_ac_hourly = pv.prod_factor

        util = Util(**self.inputs_dict)

        net_metering_limit = self.inputs_dict.get("net_metering_limit")
        if net_metering_limit > 0:
            self.net_metering = True  # used in urdb_parse

        self.dfm.add_net_metering(
            net_metering_limit=net_metering_limit,
            interconnection_limit=self.inputs_dict.get("interconnection_limit")
        )
        self.dfm.finalize()  # dfm has an evolving role, this step will most likely become internal to dfm
        self.create_economics()  # see comments in this method

        run_command = self.create_run_command(self.paths.outputs, self.xpress_model, self.dfm.DAT, False)
        run_command_bau = self.create_run_command(self.paths.outputs_bau, self.xpress_model, self.dfm.DAT_bau, True)

        log("INFO", "Initializing Command")
        command = Command(run_command)
        log("INFO", "Initializing Command BAU")
        command_bau = Command(run_command_bau)

        log("INFO", "Running Command")
        error = command.run(self.timeout)
        if error:
            output_dict['error'] = error
            return output_dict

        log("INFO", "Running BAU")
        error = command_bau.run(self.timeout)
        if error:
            output_dict['error'] = error
            return output_dict

        output_dict = self.parse_run_outputs()

        self.cleanup()

        if is_error(output_dict):
            return output_dict

        ins_and_outs_dict = self._add_inputs(output_dict)
        return ins_and_outs_dict

    def _add_inputs(self, od):
        for k in self.inputs(full_list=True).keys():
            if hasattr(self, k):
                od[k] = getattr(self, k)
        return od

    def create_run_command(self, path_output, xpress_model, DATs, base_case):

        log("DEBUG", "Current Directory: " + os.getcwd())
        log("INFO", "Creating output directory: " + path_output)

        # base case
        base_string = ""
        if base_case:
            base_string = "Base"

        # RE case
        header = 'exec '
        xpress_model_path = os.path.join(self.paths.xpress, xpress_model)

        # Command line constants and Dat file overrides
        outline = ''
        for constant in self.command_line_constants:
            outline = ' '.join([outline, constant.strip('\n')])

        for dat_file in DATs:
            if dat_file is not None:
                outline = ' '.join([outline, dat_file.strip('\n')])

        outline.replace('\n', '')

        cmd = r"mosel %s '%s' %s OutputDir='%s' ScenarioPath='%s' BaseString='%s'" \
                 % (header, xpress_model_path, outline, path_output, self.paths.inputs, base_string)

        log("DEBUG", "Returning Process Command " + cmd)

        # write a cmd file for easy debugging
        filename = self.file_cmd_input
        if base_case:
            filename = self.file_cmd_input_bau

        f = open(filename, 'w')
        f.write(cmd)
        f.close()

        return cmd

    def parse_run_outputs(self):
       
        if os.path.exists(self.file_output):
            process_results = Results(self.paths.templates, self.paths.outputs, self.paths.outputs_bau,
                                      self.paths.static_outputs, self.load_year)

            output_dict = process_results.get_output()
            output_dict['run_input_id'] = self.run_input_id

            for k,v in self.__dict__.items():
                if output_dict.get(k) is None and k in outputs():
                    output_dict[k] = v

        else:
            msg = "Output file: " + self.file_output + " does not exist"
            output_dict = {'Error': [msg] }
            log("DEBUG", "Current directory: " + os.getcwd())
            log("WARNING", msg)

        return output_dict

    def cleanup(self):
        # do not call until alternate means of accessing data is developed!
        if not self.debug:
            log("INFO", "Cleaning up folders from: " + self.paths.run)
            shutil.rmtree(self.paths.run)

   # BAU files

    # DAT2 - Economics
    def create_economics(self):
        """
        Economics are now entirely created by DatFileManager.

        The old method for creating economics.dat was setting CapCostSegCount for the BAU case equal to the
        with-tech case. This did not cause any problems because the with-tech CapCostSegCount has always been greater
        than or equal to the BAU CapCostSegCount (and Xpress will dynamically build out any arrays that dimension from
        CapCostSegCount, i.e. `Seg`).  NOT FIXED YET: NEED TO USE command_line_constants_bau

        It appears that the only attributes from the Economics class that are being passed back as outputs are
        pv_macrs_itc_reduction and batt_macrs_itc_reduction.

        :return:
        """

        self.pv_macrs_itc_reduction = 0.5
        self.batt_macrs_itc_reduction = 0.5

        # add CapCostSegCount to command line args, this functionality will move to REopt class (using DFM)
        self.command_line_constants.append(str(self.dfm.command_line_args[0]))  # only one so far
        # self.command_line_constants_bau.append(str(self.dfm.command_line_args_bau[0]))  # only one so far

    # DAT3 & DAT4 LoadSize, LoadProfile
    def create_loads(self):
        """
        api_definitions.py requires either load_profile_name & load_size
        or load_8760_kw (and load_year, not used here).
        load_profile is modified if user provides crit_load_factor, outage_start, & outage_end.
        :return: None
        """

        lp = LoadProfile(user_profile=self.inputs_dict.get('load_8760_kw'), **self.inputs_dict)
        self.load_8760_kw = lp.unmodified_load_list  # this step is needed to preserve load profile that is unmodified for outage

        log("INFO", "Creating loads.  "
                     "LoadSize: " + ("None" if self.load_size is None else str(self.load_size)) +
            ", LoadProfile: " + ("None" if self.load_profile_name is None else self.load_profile_name) +
            ", Load 8760 Specified: " + ("No" if self.load_8760_kw is None else "Yes") +
            ", Load Monthly Specified: " + ("No" if self.load_monthly_kwh is None else "Yes"))

    def create_utility(self):

        elec_tariff = ElecTariff(self.run_input_id, paths=self.paths, **self.inputs_dict) # <-- move to Util? need to take care of code below
        self.utility_name = elec_tariff.utility_name
        self.rate_name = elec_tariff.rate_name

        # command line constants will move to REopt class (using DFM)
        self.command_line_constants.append('NumRatchets=' + str(elec_tariff.reopt_args.demand_num_ratchets))
        self.command_line_constants.append('FuelBinCount=' + str(elec_tariff.reopt_args.energy_tiers_num))
        self.command_line_constants.append('DemandBinCount=' + str(elec_tariff.reopt_args.demand_tiers_num))
