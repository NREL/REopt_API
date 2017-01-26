# python libraries
import os
import traceback
import shutil
import math
import pandas as pd
from datetime import datetime, timedelta
import re
# logging
from log_levels import log
import logging

# user defined
import economics
import pvwatts
from api_definitions import *

from urdb_parse import *
from exceptions import SubprocessTimeoutError
from utilities import Command

def alphanum(s):
    return re.sub(r'\W+', '', s)


class DatLibrary:

    max_big_number = 100000000
    timeout = 60
    timed_out = False

    # if need to debug, change to True, outputs OUT files, GO files, debugging to cmdline
    debug = False
    logfile = "reopt_api.log"
    xpress_model = "REoptTS1127_PVBATT72916.mos"
    xpress_model_bau = "REoptTS1127_Util_Only.mos"
    year = 2017
    time_steps_per_hour = 1

    # DAT files to overwrite
    DAT = [None] * 20
    DAT_bau = [None] * 20

    @staticmethod
    def write_var(f, var, dat_var):
        f.write(dat_var + ": [\n")
        if isinstance(var, list):
            for i in var:
                f.write(str(i) + "\t,\n")
        else:
            f.write(str(var) + "\t,\n")
        f.write("]\n")

    def write_single_variable(self, path, var, dat_var):
        log("DEBUG", "Writing " + dat_var + " to " + path)
        f = open(path, 'w')
        self.write_var(f, var, dat_var)
        f.close()

    def get_egg(self):
        # when deployed, runs from egg file, need to update if version changes!
        #egg_name = "reopt_api-1.0-py2.7.egg"
        wd = os.getcwd()
        return wd
    
    def inputs(self,**args):
        return inputs(**args)

    def outputs(self,**args):
        return outputs(**args)

    def __init__(self,run_input_id, lib_inputs):

        self.run_input_id = run_input_id
        self.path_egg = self.get_egg()

        self.path_xpress = os.path.join(self.path_egg, "Xpress")
        self.file_logfile = os.path.join(self.path_egg, 'log', self.logfile)
        self.path_dat_library = os.path.join(self.path_xpress, "DatLibrary")
        self.path_run = os.path.join(self.path_xpress,"Run"+str(self.run_input_id))
        
        self.path_run_inputs = os.path.join(self.path_run, "Inputs")
        self.path_run_outputs = os.path.join(self.path_run,"Outputs")
        self.path_run_outputs_bau = os.path.join(self.path_run,"Outputs_bau")

        if os.path.exists(self.path_run):
            shutil.rmtree(self.path_run)
        
        for f in [self.path_run,self.path_run_inputs,self.path_run_outputs, self.path_run_outputs_bau]:
            os.mkdir(f)

        self.file_output = os.path.join(self.path_run_outputs, "summary.csv")
        self.file_output_bau = os.path.join(self.path_run_outputs_bau, "summary.csv")
        
        self.file_economics = os.path.join(self.path_run_inputs,'economics_' + str(self.run_input_id) + '.dat')
        self.file_economics_bau = os.path.join(self.path_run_inputs, 'economics_' + str(self.run_input_id) + '_bau.dat')
        self.file_gis = os.path.join(self.path_run_inputs, 'GIS_' + str(self.run_input_id) + '.dat')
        self.file_gis_bau = os.path.join(self.path_run_inputs, 'GIS_' + str(self.run_input_id) + '_bau.dat')
        self.file_load_size = os.path.join(self.path_run_inputs, 'LoadSize_' + str(self.run_input_id) + '.dat')
        self.file_load_profile = os.path.join(self.path_run_inputs, 'Load8760_' + str(self.run_input_id) + '.dat')

        self.path_utility  = os.path.join(self.path_run_inputs)
        self.path_various = os.path.join(self.path_run_inputs)

        self.folder_utility = os.path.join(self.path_dat_library, "Utility")
        self.folder_load_profile = os.path.join(self.path_dat_library, "LoadProfiles")
        self.folder_load_size = os.path.join(self.path_dat_library, "LoadSize")
        self.folder_various = os.path.join(self.path_dat_library, "Various")

        for k,v in self.inputs(full_list=True).items():
            if k == 'load_profile_name' and lib_inputs.get(k) is not None:
                setattr(self, k, lib_inputs.get(k).replace(" ", ""))

            elif lib_inputs.get(k) is  None:
                setattr(self, k, self.inputs()[k].get('default'))

            else:
                setattr(self, k, lib_inputs.get(k))

        if self.tilt is None:
            self.tilt = self.latitude
     
        if self.urdb_rate != None:
            self.parse_urdb(self.urdb_rate)
        else:
            if None not in [self.blended_utility_rate, self.demand_charge]:
                urdb_rate = self.make_urdb_rate(self.blended_utility_rate, self.demand_charge)
                self.parse_urdb(urdb_rate)

        self.default_load_profiles = [p.lower() for p in default_load_profiles()]
        self.default_building = default_building()
        self.default_city = default_cities()[0]
        if self.latitude is not None and self.longitude is not None:
            self.default_city = default_cities()[self.localize_load()] 

        for k in self.outputs() :
            setattr(self, k, None)
        self.update_types()
        self.setup_logging()

    def update_types(self):
        for group in [self.inputs(full_list=True),self.outputs()]:
            for k,v in group.items():
                value = getattr(self,k)

                if value is not None:
                    if v['type']==float:
                        if v['pct']:
                            if value > 1.0:
                                setattr(self, k, float(value)*0.01)

                    elif v['type'] == list:
                        value = [float(i) for i in getattr(self, k)]
                        setattr(self, k, value)

                    else:
                        setattr(self,k,v['type'](value))

    def get_subtask_inputs(self, name):
        output = {}
        defaults = self.inputs(filter=name)

        for k in defaults.keys():
            output[k] = getattr(self,k)
            if output[k] is None:
                default = defaults[k].get('default')
                if default is not None:
                    output[k] = default

        return output

    def run(self):

        self.create_constant_bau()
        self.create_economics()
        self.create_loads()
        self.create_GIS()
        self.create_utility()

        run_command = self.create_run_command(self.path_run_outputs, self.xpress_model, self.DAT )
        run_command_bau = self.create_run_command(self.path_run_outputs_bau, self.xpress_model_bau, self.DAT_bau )
        
        log("DEBUG", "Initializing Command")
        command = Command(run_command)
        log("DEBUG", "Initializing Command BAU")
        command_bau = Command(run_command_bau)
        
        log("DEBUG", "Running Command")
        command.run(self.timeout)
        log("DEBUG", "Running BAU")
        command_bau.run(self.timeout)

        self.parse_run_outputs()
        self.cleanup()
        return self.lib_output()

    def lib_output(self):
        output =  {'run_input_id':self.run_input_id}
        for k in self.inputs(full_list=True).keys()  +  self.outputs().keys():
            if hasattr(self,k):
                output[k] = getattr(self,k)
            else:
                output[k] = None
        return output

    def setup_logging(self):
        logging.basicConfig(filename=self.file_logfile,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M%S %p',
                            level=logging.DEBUG)

    def create_run_command(self, path_output, xpress_model, DATs ):

        log("DEBUG", "Current Directory: " + os.getcwd())
        log("DEBUG", "Creating output directory: " + path_output)

        # RE case
        header = 'exec '
        header += os.path.join(self.path_xpress,xpress_model)
           
        outline = ''

        for dat_file in DATs:
            if dat_file is not None:
                outline = ', '.join([outline, dat_file.strip('\n')])
        
        outline.replace('\n', '') 
        
        output = r"%s %s, OutputDir='%s', DatLibraryPath='%s', LocalPath='%s'" % (header, outline, path_output, self.path_dat_library, self.path_egg)
     	output_txt = """ "%s " """ % (output)
        
        log("DEBUG", "Returning Process Command " + output)
        return ['mosel', '-c', output]

    def parse_run_outputs(self):
        if os.path.exists(self.file_output):
            df = pd.read_csv(self.file_output, header=None, index_col=0)
            df = df.transpose()
            pv_size = 0

            if 'LCC' in df.columns:
                self.lcc = float(df['LCC'].values[0])
            if 'BattInverter_kW' in df.columns:
                self.batt_kw = float(df['BattInverter_kW'].values[0])
            if 'BattSize_kWh' in df.columns:
                self.batt_kwh = float(df['BattSize_kWh'].values[0])
            if 'PVNMsize_kW' in df.columns:
                pv_size += float(df['PVNMsize_kW'].values[0])
            if 'PVsize_kW' in df.columns:
                pv_size += float(df['PVsize_kW'].values[0])
            if 'Utility_kWh' in df.columns:
                self.utility_kwh = float(df['Utility_kWh'].values[0])

            self.update_types()

            if pv_size > 0:
                self.pv_kw = str(round(pv_size, 0))
            else:
                self.pv_kw = 0

        else:
            log("DEBUG", "Current directory: " + os.getcwd())
            log("WARNING", "Output file: " + self.file_output + " + doesn't exist!")

        if os.path.exists(self.file_output_bau):
            df = pd.read_csv(self.file_output_bau, header=None, index_col=0)
            df = df.transpose()
           
            if 'LCC' in df.columns:
                self.npv = float(df['LCC'].values[0]) - float(self.lcc)
            else:
                self.npv = 0

    def cleanup(self):
        return
        log("DEBUG", "Cleaning up folders from: " + os.getcwd())
        log("DEBUG", "Output folder: " + self.path_run_outputs)

        if not self.debug:
            for f in [self.path__run_output]:
                if os.path.exists(f):
                    shutil.rmtree(f, ignore_errors=True)

            for p in [self.file_economics,self.file_economics_bau, self.file_gis, self.file_gis_bau, self.file_load_profile, self.file_load_size]:
                if os.path.exists(p):
                    os.remove(p)

    # BAU files
    def create_constant_bau(self):
        self.DAT_bau[0] = "DAT1=" + "'" + os.path.join(self.folder_various, 'constant_bau.dat') + "'"
        self.DAT_bau[5] = "DAT6=" + "'" + os.path.join(self.folder_various, 'storage_bau.dat') + "'"
        self.DAT_bau[6] = "DAT7=" + "'" + os.path.join(self.folder_various, 'maxsizes_bau.dat') + "'"

    # DAT2 - Economics
    def create_economics(self):

        econ_inputs = self.get_subtask_inputs('economics')

        fp = self.file_economics
        econ = economics.Economics(econ_inputs, file_path=fp,business_as_usual=False)

        for k in ['analysis_period','pv_cost','pv_om','batt_cost_kw','batt_replacement_cost_kw',
                  'batt_replacement_cost_kwh','owner_discount_rate','offtaker_discount_rate']:
           setattr(self, k, getattr(econ,k))

        self.DAT[1] = "DAT2=" + "'" + self.file_economics + "'"

        fp = self.file_economics_bau
        econ = economics.Economics(econ_inputs, file_path=fp, business_as_usual=True)
        self.DAT_bau[1] = "DAT2=" + "'" + self.file_economics_bau + "'"

    # DAT3 & DAT4 LoadSize, LoadProfile
    def create_loads(self):

        default_load_profile = "Load8760_raw_" + self.default_city + "_" + self.default_building + ".dat"
        default_load_profile_norm = "Load8760_norm_" + self.default_city + "_" + self.default_building + ".dat"
        default_load_size = "LoadSize_" + self.default_city + "_" + self.default_building + ".dat"

        log("DEBUG", "Creating loads.  "
                     "LoadSize: " + ("None" if self.load_size is None else str(self.load_size)) +
                     ", LoadProfile: " + ("None" if self.load_profile_name is None else self.load_profile_name) +
                     ", Load 8760 Specified: " + ("No" if self.load_8760_kw is None else "Yes") +
                     ", Load Monthly Specified: " + ("No" if self.load_monthly_kwh is None else "Yes"))

        if self.load_8760_kw is not None:
            if len(self.load_8760_kw) == 8760:
                self.load_size = sum(self.load_8760_kw)
                self.write_single_variable(self.file_load_size, self.load_size, "AnnualElecLoad")
                self.write_single_variable(self.file_load_profile, self.load_8760_kw, "LoadProfile")
               
            else:
                log("ERROR", "Load profile uploaded contains: " + len(self.load_8760_kw) + " values, 8760 required")

        if self.load_monthly_kwh is not None:
            if len(self.load_monthly_kwh) == 12:
                self.load_size = float(sum(self.load_monthly_kwh))
                self.write_single_variable(self.file_load_size,self.load_size, "AnnualElecLoad")
                
                if (self.load_profile_name is not None) and (self.load_profile_name.lower() in self.default_load_profiles):
                        name = "Load8760_norm_" + self.default_city + "_" + self.load_profile_name + ".dat"
                        path = os.path.join( self.folder_load_profile , name )
                        load_profile = self.scale_load_by_month(path)
                else:
                    path = os.path.join( self.folder_load_profile, default_load_profile_norm)
                    load_profile = self.scale_load_by_month(path)

		self.write_single_variable(self.file_load_profile, load_profile, "LoadProfile"  )
            
            else:
                log("ERROR", "Load profile uploaded contains: " + str(len(self.load_monthly_kwh)) + " values, 12 required")

        if self.load_8760_kw is None and self.load_monthly_kwh is None:
            if self.load_size is None:

	        self.file_load_size = os.path.join( self.folder_load_size, default_load_size)
                self.file_load_profile = os.path.join( self.folder_load_profile, default_load_profile) 

                # Load profile with no load size
                if self.load_profile_name is not None:
                    if self.load_profile_name.lower() in self.default_load_profiles:
                        filename_profile = "Load8760_raw_" + self.default_city + "_" + self.load_profile_name + ".dat"
                        filename_size = "LoadSize_" + self.default_city + "_" + self.load_profile_name + ".dat"
                        self.file_load_size = os.path.join( self.folder_load_size , filename_size)
                        self.file_load_profile = os.path.join( self.folder_load_profile , filename_profile)
                
            else:
                self.write_single_variable(self.file_load_size, self.load_size, "AnnualElecLoad")
		
                # Load profile specified, with load size specified
                if self.load_profile_name is not None:
                    if self.load_profile_name.lower() in self.default_load_profiles:
                        tmp_profile = os.path.join( self.folder_load_profile, "Load8760_norm_" + self.default_city + "_" + self.load_profile_name + ".dat")
                        load_profile = self.scale_load(tmp_profile, self.load_size)
                
                #Load size specified, no profile
                else:
		    p = os.path.join( self.folder_load_profile, default_load_profile)
                    load_profile = self.scale_load(p, self.load_size)

		self.write_single_variable(self.file_load_profile, load_profile, "LoadProfile")

        self.DAT[2] = "DAT3=" + "'" + self.file_load_size + "'"
        self.DAT_bau[2] = self.DAT[2]
        self.DAT[3] = "DAT4=" + "'" + self.file_load_profile + "'"
        self.DAT_bau[3] = self.DAT[3]

    def scale_load(self, file_load_profile, scale_factor):
        
        load_profile = []
        f = open(file_load_profile, 'r')
        for line in f:
            load_profile.append(float(line.strip('\n')) * scale_factor)

        # fill in W, X, S bins
        for _ in range(8760*3):
            load_profile.append(self.max_big_number)

        return load_profile

    def scale_load_by_month(self, profile_file):
      
        load_profile = []
        f = open(profile_file, 'r')

        datetime_current = datetime(self.year, 1, 1, 0)
        month_total = 0
        month_scale_factor = []
        normalized_load = []

        for line in f:
            month = datetime_current.month
            normalized_load.append(float(line.strip('\n')))
            month_total += self.load_size * float(line.strip('\n'))

            # add an hour
            datetime_current = datetime_current + timedelta(0, 0, 0, 0, 0, 1, 0)

            if month != datetime_current.month:
                month_scale_factor.append(float(self.load_monthly_kwh[month - 1] / month_total))
                month_total = 0

                log("DEBUG", "Monthly kwh: " + str(self.load_monthly_kwh[month - 1]) +
                    ", Month scale factor: " + str(month_scale_factor[month - 1]) +
                    ", Annual load: " + str(self.load_size))

        datetime_current = datetime(self.year, 1, 1, 0)
        for load in normalized_load:
            month = datetime_current.month

            load_profile.append(self.load_size * load * month_scale_factor[month - 1])

            # add an hour
            datetime_current = datetime_current + timedelta(0, 0, 0, 0, 0, 1, 0)

        # fill in W, X, S bins
        for _ in range(8760*3):
            load_profile.append(self.max_big_number)

        return load_profile

    def localize_load(self):

        min_distance = self.max_big_number
        min_index = 0

        idx = 0
        for _ in default_cities():
            lat = default_latitudes()[idx]
            lon = default_longitudes()[idx]
            lat_dist = self.latitude - lat
            lon_dist = self.longitude - lon

            distance = math.sqrt(math.pow(lat_dist, 2) + math.pow(lon_dist, 2))
            if distance < min_distance:
                min_distance = distance
                min_index = idx

            idx += 1

        return min_index

    def create_GIS(self):

        if self.latitude is not None and self.longitude is not None:

            pv_inputs = self.get_subtask_inputs('pvwatts')
            GIS = pvwatts.PVWatts(self.path_run_inputs, pv_inputs)

            self.DAT[4] = "DAT5=" + "'" + self.file_gis + "'"
            self.DAT_bau[4] = "DAT5=" + "'" + self.file_gis_bau + "'"

    def create_utility(self):
        if self.utility_name is not None and self.rate_name is not None:
            self.path_util_rate = os.path.join(self.path_utility,self.utility_name, self.rate_name)

            with open(os.path.join(self.path_util_rate, "NumRatchets.dat"), 'r') as f:
                num_ratchets = str(f.readline())
            
            with open(os.path.join(self.path_util_rate, "bins.dat"), 'r') as f:
                fuel_bin_count = str(f.readline())
                demand_bin_count = str(f.readline())

            self.DAT[7] = num_ratchets
            self.DAT_bau[7] = self.DAT[7]
            self.DAT[8] = "UtilName=" + "'" + str(self.utility_name) + "'"
            self.DAT_bau[8] = self.DAT[8]
            self.DAT[9] = "UtilRate=" + "'" + str(self.rate_name) + "'"
            self.DAT_bau[9] = self.DAT[9]
            self.DAT[10] = fuel_bin_count
            self.DAT_bau[10] = self.DAT[10]
            self.DAT[11] = demand_bin_count
            self.DAT_bau[11] = self.DAT[11]

    def parse_urdb(self, urdb_rate):

        utility_name = alphanum(urdb_rate['utility'])
        rate_name = alphanum(urdb_rate['name'])

        base_folder = os.path.join(self.path_run_inputs, utility_name)
        if os.path.exists(base_folder):
            shutil.rmtree(base_folder)
        os.mkdir(base_folder)

        rate_output_folder = os.path.join(base_folder, rate_name)
        os.mkdir(rate_output_folder)

        with open(os.path.join(rate_output_folder, 'json.txt'), 'w') as outfile:
            json.dump(urdb_rate, outfile)
            outfile.close()
        
        with open(os.path.join(rate_output_folder, 'rate_name.txt'), 'w') as outfile:
            outfile.write(str(rate_name).replace(' ', '_'))
            outfile.close()

        log_root = os.path.join(self.path_egg, 'log')
        urdb_parse = UrdbParse(self.path_run_inputs, log_root, self.year, self.time_steps_per_hour)
        urdb_parse.parse_specific_rates([utility_name], [rate_name])

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
        print urdb_rate
        return urdb_rate
