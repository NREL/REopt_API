# python libraries
# some libraries are being imported via the 'import *' statements below
# including at least 'os' and 'json'
import re
import shutil

# user defined
import economics
from api_definitions import *
from reo.src.dat_file_manager import DatFileManager
from reo.src.techs import PV, Util
from reo.src.load_profile import LoadProfile
from results import Results
from urdb_parse import *
from utilities import Command, check_directory_created, write_single_variable, is_error


def alphanum(s):
    return re.sub(r'\W+', '', s)


class DatLibrary:
    """
    Instantiated in models.py within RunInput.create_output,
    which in turn is called by RunInputResource.obj_create in api.py
    """

    # statically constant
    max_big_number = 100000000

    # timeout is slightly less than server timeout of 5 minutes by default
    timed_out = False

    # if need to debug, change to True, outputs OUT files, GO files, debugging to cmdline
    debug = True
    logfile = "reopt_api.log"
    xpress_model = "REopt_API.mos"
    time_steps_per_hour = 1

    def get_egg(self):
        wd = os.getcwd()
        return wd

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

        self.timed_out = False
        self.net_metering = False

        # DAT files to overwrite
        self.DAT = [None] * 20
        self.DAT_bau = [None] * 20

        # Command line constants
        self.command_line_constants = list()
        self.command_line_constants.append("ScenarioNum=" + str(run_input_id))

        # Economic inputs and calculated vals
        self.economics = list()

        self.run_input_id = run_input_id
        self.path_egg = self.get_egg()

        self.path_templates = os.path.join(self.path_egg, "reo", "templates")
        self.path_xpress = os.path.join(self.path_egg, "Xpress")
        self.file_logfile = os.path.join(self.path_egg, 'log', self.logfile)

        self.path_dat_library = os.path.join(self.path_xpress, "DatLibrary")
        self.path_run = os.path.join(self.path_xpress, "Run" + str(self.run_input_id))
        self.path_files_to_download = os.path.join(self.path_xpress, "Downloads")

        self.path_run_inputs = os.path.join(self.path_run, "Inputs")
        self.path_run_outputs = os.path.join(self.path_run, "Outputs")
        self.path_run_outputs_bau = os.path.join(self.path_run, "Outputs_bau")
        self.path_static_outputs = os.path.join(self.path_egg, "static", "files", str(run_uuid))

        if os.path.exists(self.path_run):
            shutil.rmtree(self.path_run)

        for f in [self.path_run, self.path_run_inputs, self.path_run_outputs, self.path_run_outputs_bau,
                  self.path_static_outputs]:
            os.mkdir(f)

        check_directory_created(self.path_run)
        check_directory_created(self.path_run_inputs)
        check_directory_created(self.path_run_outputs)
        check_directory_created(self.path_run_outputs_bau)

        self.file_output = os.path.join(self.path_run_outputs, "REopt_results.json")

        self.file_post_input = os.path.join(self.path_run_inputs, "POST.json")
        self.file_cmd_input = os.path.join(self.path_run_inputs, "cmd.log")
        self.file_cmd_input_bau = os.path.join(self.path_run_inputs, "cmd_bau.log")
        self.file_constant = os.path.join(self.path_run_inputs, 'constant_' + str(self.run_input_id) + '.dat')
        self.file_constant_bau = os.path.join(self.path_run_inputs, 'constant_' + str(self.run_input_id) + '_bau.dat')
        self.file_storage = os.path.join(self.path_run_inputs, 'storage_' + str(self.run_input_id) + '.dat')
        self.file_storage_bau = os.path.join(self.path_run_inputs, 'storage_' + str(self.run_input_id) + '_bau.dat')
        self.file_max_size = os.path.join(self.path_run_inputs, 'maxsizes_' + str(self.run_input_id) + '.dat')
        self.file_max_size_bau = os.path.join(self.path_run_inputs, 'maxsizes_' + str(self.run_input_id) + '_bau.dat')
        self.file_economics = os.path.join(self.path_run_inputs, 'economics_' + str(self.run_input_id) + '.dat')
        self.file_economics_bau = os.path.join(self.path_run_inputs, 'economics_' + str(self.run_input_id) + '_bau.dat')
        self.file_gis = os.path.join(self.path_run_inputs, 'GIS_' + str(self.run_input_id) + '.dat')
        self.file_gis_bau = os.path.join(self.path_run_inputs, 'GIS_' + str(self.run_input_id) + '_bau.dat')
        self.file_load_size = os.path.join(self.path_run_inputs, 'LoadSize_' + str(self.run_input_id) + '.dat')
        self.file_load_profile = os.path.join(self.path_run_inputs, 'Load8760_' + str(self.run_input_id) + '.dat')
        self.file_NEM = os.path.join(self.path_run_inputs, 'NMIL_' + str(self.run_input_id) + '.dat')

        self.path_utility = os.path.join(self.path_run_inputs, "Utility")
        self.path_various = os.path.join(self.path_run_inputs)

        self.folder_utility = os.path.join(self.path_dat_library, "Utility")
        self.folder_load_profile = os.path.join(self.path_dat_library, "LoadProfiles")
        self.folder_load_size = os.path.join(self.path_dat_library, "LoadSize")
        self.folder_various = os.path.join(self.path_dat_library, "Various")

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

        self.dfm = DatFileManager()
        self.dfm.run_id = self.run_input_id  # dfm is a singleton
        self.dfm.path_inputs = self.path_run_inputs
        self.dfm.n_timesteps = inputs_dict['time_steps_per_hour'] * 8760

    def log_post(self, json_POST):
        with open(self.file_post_input, 'w') as file_post:
            json.dump(json_POST, file_post)

    def get_path_run(self):
        return self.path_run

    def get_path_run_inputs(self):
        return self.path_run_inputs

    def get_path_run_outputs(self):
        return self.path_run_outputs

    def get_path_run_outputs_bau(self):
        return self.path_run_outputs_bau

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

        self.create_simple_bau()
        self.create_constants()
        self.create_storage()
        self.create_size_limits()
        self.create_economics()
        self.create_loads()
        self.create_nem()
        self.create_utility()

        solar_data = self.create_Solar()
        self.pv_kw_ac_hourly = solar_data

        run_command = self.create_run_command(self.path_run_outputs, self.xpress_model, self.DAT, False)
        run_command_bau = self.create_run_command(self.path_run_outputs_bau, self.xpress_model, self.DAT_bau, True)

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
        xpress_model_path = os.path.join(self.path_xpress, xpress_model)

        # Command line constants and Dat file overrides
        outline = ''
        for constant in self.command_line_constants:
            outline = ' '.join([outline, constant.strip('\n')])

        for dat_file in DATs:
            if dat_file is not None:
                outline = ' '.join([outline, dat_file.strip('\n')])

        outline.replace('\n', '')

        cmd = r"mosel %s '%s' %s OutputDir='%s' DatLibraryPath='%s' ScenarioPath='%s' BaseString='%s'" \
                 % (header, xpress_model_path, outline, path_output, self.path_dat_library, self.path_run_inputs, base_string)

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
            process_results = Results(self.path_templates, self.path_run_outputs, self.path_run_outputs_bau,
                                      self.path_static_outputs, self.economics, self.load_year)

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
            log("INFO", "Cleaning up folders from: " + self.path_run)
            shutil.rmtree(self.path_run)

   # BAU files
    def create_simple_bau(self):
        self.DAT_bau[0] = "DAT1=" + "'" + self.file_constant_bau + "'"
        self.DAT_bau[6] = "DAT7=" + "'" + self.file_max_size_bau + "'"

        shutil.copyfile(os.path.join(self.folder_various, 'constant_bau.dat'), self.file_constant_bau)
        shutil.copyfile(os.path.join(self.folder_various, 'maxsizes_bau.dat'), self.file_max_size_bau)

    # Constant file
    def create_constants(self):

        can_grid_charge = getattr(self, "batt_can_gridcharge", 1)

        Tech = ['PV', 'PVNM', 'UTIL1']
        TechIsGrid = [0, 0, 1]
        Load = ['1R', '1W', '1X', '1S']
        TechToLoadMatrix = [1, 1, 1, 1, \
                            1, 1, 1, 1, \
                            1, 0, 0, int(can_grid_charge)]
        TechClass = ['PV', 'UTIL']
        NMILRegime = ['BelowNM', 'NMtoIL', 'AboveIL']
        TechToNMILMapping = [1, 0, 0, \
                             0, 1, 0, \
                             0, 0, 0]
        TurbineDerate = [1, 1, 0]
        TechToTechClassMatrix = [1, 0, \
                                 1, 0, \
                                 0, 0]

        self.DAT[0] = "DAT1=" + "'" + self.file_constant + "'"

        write_single_variable(self.file_constant, Tech, 'Tech')
        write_single_variable(self.file_constant, TechIsGrid, 'TechIsGrid', 'a')
        write_single_variable(self.file_constant, Load, 'Load', 'a')
        write_single_variable(self.file_constant, TechToLoadMatrix, 'TechToLoadMatrix', 'a')
        write_single_variable(self.file_constant, TechClass, 'TechClass', 'a')
        write_single_variable(self.file_constant, NMILRegime, 'NMILRegime', 'a')
        write_single_variable(self.file_constant, TechToNMILMapping, 'TechToNMILMapping', 'a')
        write_single_variable(self.file_constant, TurbineDerate, 'TurbineDerate', 'a')
        write_single_variable(self.file_constant, TechToTechClassMatrix, 'TechToTechClassMatrix', 'a')

    # storage
    def create_storage(self):
        """
        writes storage_[run_input_id].dat, which contains:
            StorageMinChargePcent
            EtaStorIn  (same as roundtrip efficiency)
            EtaStorOut (currently not used in REopt)
            BattLevelCoef
            InitSOC
        NOTE: EtaStorIn and EtaStorOut are array(Tech,Load)
        """
        Tech = ['PV', 'PVNM', 'UTIL1']  # copied from create_constants, needs to adjusted for future techs
        Load = ['1R', '1W', '1X', '1S']

        self.DAT[5] = "DAT6=" + "'" + self.file_storage + "'"

        roundtrip_efficiency = self.batt_efficiency * self.batt_inverter_efficiency * self.batt_rectifier_efficiency

        etaStorIn = list()
        etaStorOut = list()
        for t in Tech:
            for ld in Load:
                etaStorIn.append(roundtrip_efficiency if ld is '1S' else 1)
                etaStorOut.append(roundtrip_efficiency if ld is '1S' else 1)

        write_single_variable(self.file_storage, self.batt_soc_min, 'StorageMinChargePcent')
        write_single_variable(self.file_storage, etaStorIn, 'EtaStorIn', mode='a')
        write_single_variable(self.file_storage, etaStorOut, 'EtaStorOut', mode='a')
        write_single_variable(self.file_storage, [-1, 0], 'BattLevelCoef', mode='a')
        write_single_variable(self.file_storage, self.batt_soc_init, 'InitSOC', mode='a')

        # NOTE: All bau dat files except maxsizes can be eliminated by just placing zeros in maxsizes_bau.dat
        # (including all utility bau files)
        self.DAT_bau[5] = "DAT6=" + "'" + self.file_storage_bau + "'"
        Tech_bau = ['UTIL1']
        etaStorIn_bau = list()
        etaStorOut_bau = list()
        for t in Tech_bau:
            for ld in Load:
                etaStorIn_bau.append(roundtrip_efficiency if ld is '1S' else 1)
                etaStorOut_bau.append(roundtrip_efficiency if ld is '1S' else 1)

        write_single_variable(self.file_storage_bau, self.batt_soc_min, 'StorageMinChargePcent')
        write_single_variable(self.file_storage_bau, etaStorIn_bau, 'EtaStorIn', mode='a')
        write_single_variable(self.file_storage_bau, etaStorOut_bau, 'EtaStorOut', mode='a')
        write_single_variable(self.file_storage_bau, [-1, 0], 'BattLevelCoef', mode='a')
        write_single_variable(self.file_storage_bau, self.batt_soc_init, 'InitSOC', mode='a')

    # DAT2 - Economics
    def create_economics(self):

        econ_inputs = self.get_subtask_inputs('economics')

        fp = self.file_economics
        self.economics = economics.Economics(file_path=fp, business_as_usual=False,**econ_inputs)

        for k in self.economics.__dict__.keys():
            setattr(self, k, getattr(self.economics, k))

        self.DAT[1] = "DAT2=" + "'" + self.file_economics + "'"

        fp = self.file_economics_bau
        econ = economics.Economics(file_path=fp, business_as_usual=True,**econ_inputs)

        self.DAT_bau[1] = "DAT2=" + "'" + self.file_economics_bau + "'"
        self.command_line_constants.append("CapCostSegCount=" + str(self.cap_cost_segments))

    # DAT3 & DAT4 LoadSize, LoadProfile
    def create_loads(self):
        """
        api_definitions.py requires either load_profile_name & load_size
        or load_8760_kw (and load_year, not used here).
        load_profile is modified if user provides crit_load_factor, outage_start, & outage_end.
        :return: None
        """

        lp = LoadProfile(user_profile=self.inputs_dict.get('load_8760_kw'), **self.inputs_dict)

        log("INFO", "Creating loads.  "
                     "LoadSize: " + ("None" if self.load_size is None else str(self.load_size)) +
            ", LoadProfile: " + ("None" if self.load_profile_name is None else self.load_profile_name) +
            ", Load 8760 Specified: " + ("No" if self.load_8760_kw is None else "Yes") +
            ", Load Monthly Specified: " + ("No" if self.load_monthly_kwh is None else "Yes"))

        self.DAT[2] = "DAT3=" + "'" + self.file_load_size + "'"
        self.DAT_bau[2] = self.DAT[2]
        self.DAT[3] = "DAT4=" + "'" + self.file_load_profile + "'"
        self.DAT_bau[3] = self.DAT[3]

    def create_Solar(self):

        pv = PV(**self.inputs_dict)
        util = Util(**self.inputs_dict)

        self.dfm.finalize()  # needed for ProdFactor (depends on which Techs are defined)

        solar_data = pv.prod_factor

        self.DAT[4] = "DAT5=" + "'" + self.file_gis + "'"
        self.DAT_bau[4] = "DAT5=" + "'" + self.file_gis_bau + "'"

        return solar_data

    def create_size_limits(self):

        acres_per_MW = 6
        squarefeet_to_acre = 2.2957e-5
        total_acres = 0

        # Internal working defaults, probably need to revamp and move to api_definitions.py
        pv_kw_min = 0
        pv_kw_max = 200000
        util_kw_max = 12000000

        batt_kw_min = 0
        batt_kwh_min = 0
        batt_kw_max = 10000
        batt_kwh_max = 10000


        # pv max size based on user input
        if self.pv_kw_max is not None:
            pv_kw_max = self.pv_kw_max
        else:
            # don't restrict unless they specify both land_area and roof_area, otherwise one of them is "unlimited" in UI
            if self.roof_area is not None and self.land_area is not None:
                total_acres += (self.roof_area * squarefeet_to_acre) + self.land_area
                pv_kw_max = (total_acres / acres_per_MW) * 1000

        if self.pv_kw_min is not None:
            pv_kw_min = self.pv_kw_min

        if pv_kw_min > pv_kw_max:
            pv_kw_min = pv_kw_max

        # battery constraints
        if self.batt_kw_max is not None:
            batt_kw_max = self.batt_kw_max
        if self.batt_kwh_max is not None:
            batt_kwh_max = self.batt_kwh_max
        if self.batt_kw_min is not None:
            batt_kw_min = self.batt_kw_min
        if self.batt_kwh_min is not None:
            batt_kwh_min = self.batt_kwh_min

        # update outputs
        self.pv_kw_min = pv_kw_min
        self.pv_kw_max = pv_kw_max
        self.batt_kwh_min = batt_kwh_min
        self.batt_kwh_max = batt_kwh_max
        self.batt_kw_min = batt_kw_min
        self.batt_kw_max = batt_kw_max

        MaxSize = [pv_kw_max, pv_kw_max, util_kw_max]
        MinStorageSizeKW = batt_kw_min
        MinStorageSizeKWH = batt_kwh_min
        MaxStorageSizeKW = batt_kw_max
        MaxStorageSizeKWH = batt_kwh_max
        TechClassMinSize = [pv_kw_min, 0]

        write_single_variable(self.file_max_size, MaxSize, "MaxSize", 'a')
        write_single_variable(self.file_max_size, MinStorageSizeKW, "MinStorageSizeKW", 'a')
        write_single_variable(self.file_max_size, MaxStorageSizeKW, "MaxStorageSizeKW", 'a')
        write_single_variable(self.file_max_size, MinStorageSizeKWH, "MinStorageSizeKWH", 'a')
        write_single_variable(self.file_max_size, MaxStorageSizeKWH, "MaxStorageSizeKWH", 'a')
        write_single_variable(self.file_max_size, TechClassMinSize, "TechClassMinSize", 'a')

        self.DAT[6] = "DAT7=" + "'" + self.file_max_size + "'"

    def create_utility(self):

        if self.urdb_rate is not None:
            log("INFO", "Parsing URDB rate")
            self.parse_urdb(self.urdb_rate)
        else:
            if None not in [self.blended_utility_rate, self.demand_charge]:
                log("INFO", "Making URDB rate from blended data")
                urdb_rate = self.make_urdb_rate(self.blended_utility_rate, self.demand_charge)
                self.parse_urdb(urdb_rate)

        if self.utility_name is not None and self.rate_name is not None:

            utility_folder = os.path.join(self.path_utility, self.utility_name)
            rate_output_folder = os.path.join(utility_folder, self.rate_name)

            with open(os.path.join(rate_output_folder, "NumRatchets.dat"), 'r') as f:
                num_ratchets = str(f.readline())

            with open(os.path.join(rate_output_folder, "bins.dat"), 'r') as f:
                fuel_bin_count = str(f.readline())
                demand_bin_count = str(f.readline())

            self.command_line_constants.append(num_ratchets)
            self.command_line_constants.append(fuel_bin_count)
            self.command_line_constants.append(demand_bin_count)

            # for ease in the Xpress model, copy to generic Utility folder and delete sub-rate folder
            filelist = os.listdir(rate_output_folder)
            for f in filelist:
                shutil.copy2(os.path.join(rate_output_folder, f), self.path_utility)
            shutil.rmtree(utility_folder)

    def parse_urdb(self, urdb_rate):

        utility_name = alphanum(urdb_rate['utility'])
        rate_name = alphanum(urdb_rate['name'])

        base_folder = os.path.join(self.path_utility, utility_name)
        rate_output_folder = os.path.join(base_folder, rate_name)

        if os.path.exists(base_folder):
            shutil.rmtree(base_folder)

        for f in [self.path_utility, base_folder, rate_output_folder]:
            os.mkdir(f)

        check_directory_created(self.path_utility)
        check_directory_created(base_folder)
        check_directory_created(rate_output_folder)

        with open(os.path.join(rate_output_folder, 'json.txt'), 'w') as outfile:
            json.dump(urdb_rate, outfile)
            outfile.close()

        with open(os.path.join(rate_output_folder, 'utility_name.txt'), 'w') as outfile:
            outfile.write(str(utility_name).replace(' ', '_'))
            outfile.close()

        with open(os.path.join(rate_output_folder, 'rate_name.txt'), 'w') as outfile:
            outfile.write(str(rate_name).replace(' ', '_'))
            outfile.close()

        urdb_parse = UrdbParse(self.path_utility, self.load_year, self.time_steps_per_hour,
                               self.net_metering, self.wholesale_rate)
        urdb_parse.parse_specific_rates([utility_name], [rate_name])

        # Copy hourly rate summary to outputs
        if os.path.exists(urdb_parse.utility_dat_files.path_energy_cost):

            shutil.copyfile(urdb_parse.utility_dat_files.path_energy_cost,
                            os.path.join(self.path_run_outputs, urdb_parse.utility_dat_files.name_energy_cost))
            shutil.copyfile(urdb_parse.utility_dat_files.path_energy_cost,
                            os.path.join(self.path_run_outputs_bau, urdb_parse.utility_dat_files.name_energy_cost))

        if os.path.exists(urdb_parse.utility_dat_files.path_demand_cost):

            shutil.copyfile(urdb_parse.utility_dat_files.path_demand_cost,
                            os.path.join(self.path_run_outputs, urdb_parse.utility_dat_files.name_demand_cost))
            shutil.copyfile(urdb_parse.utility_dat_files.path_demand_cost,
                            os.path.join(self.path_run_outputs_bau, urdb_parse.utility_dat_files.name_demand_cost))

        self.utility_name = utility_name
        self.rate_name = rate_name

    def make_urdb_rate(self, blended_utility_rate, demand_charge):

        urdb_rate = {}

        # energy rate
        energyratestructure = []
        energyweekdayschedule = []
        energyweekendschedule = []

        flatdemandstructure = []
        flatdemandmonths = []

        unique_energy_rate = set(blended_utility_rate)
        unique_demand_rate = set(demand_charge)

        for energy_rate in unique_energy_rate:
            rate = [{'rate': energy_rate, 'unit': 'kWh'}]
            energyratestructure.append(rate)

        for demand_rate in unique_demand_rate:
            rate = [{'rate': demand_rate}]
            flatdemandstructure.append(rate)

        for month in range(0, 12):
            energy_period = 0
            demand_period = 0
            for energy_rate in unique_energy_rate:
                if energy_rate == blended_utility_rate[month]:
                    tmp = [energy_period] * 24
                    energyweekdayschedule.append(tmp)
                    energyweekendschedule.append(tmp)
                energy_period += 1
            for demand_rate in unique_demand_rate:
                if demand_rate == demand_charge[month]:
                    flatdemandmonths.append(demand_period)
                demand_period += 1

        # ouput
        urdb_rate['energyweekdayschedule'] = energyweekdayschedule
        urdb_rate['energyweekendschedule'] = energyweekendschedule
        urdb_rate['energyratestructure'] = energyratestructure

        if sum(unique_demand_rate) > 0:
            urdb_rate['flatdemandstructure'] = flatdemandstructure
            urdb_rate['flatdemandmonths'] = flatdemandmonths
            urdb_rate['flatdemandunit'] = 'kW'

        urdb_rate['label'] = self.run_input_id
        urdb_rate['name'] = "Custom_rate_" + str(self.run_input_id)
        urdb_rate['utility'] = "Custom_utility_" + str(self.run_input_id)
        return urdb_rate

    def create_nem(self):

        net_metering_limit = 0
        interconnection_limit = 1000000

        nem_input = getattr(self, "net_metering_limit")
        ic_input = getattr(self, "interconnection_limit")

        if nem_input is not None:
            net_metering_limit = nem_input
        if ic_input is not None:
            interconnection_limit = ic_input
        if net_metering_limit > 0:
            self.net_metering = True

        # check on if NM, IC are in right spot
        write_single_variable(self.file_NEM,
                                   [net_metering_limit, interconnection_limit, self.max_big_number],
                                   "NMILLimits")

        self.DAT[16] = "DAT17=" + "'" + self.file_NEM + "'"
