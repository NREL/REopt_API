import threading
import os
import subprocess
from shlex import split
from reo.log_levels import log
from reo.results import Results
from reo.src.dat_file_manager import DatFileManager


class Command(object):

    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.error = False

    def run(self, timeout):

        def target():
            self.process = subprocess.Popen(split(self.cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _, self.error = self.process.communicate()

        log("DEBUG", "XPRESS Creating Thread")
        thread = threading.Thread(target=target)

        log("DEBUG", "XPRESS Starting Thread")
        thread.start()

        log("DEBUG", "XPRESS Join Thread")
        thread.join(timeout)

        if thread.is_alive():
            log("ERROR", "XPRESS Thread Timeout")
            self.process.terminate()
            thread.join()
            raise RuntimeError('reopt', "REopt optimization exceeded timeout: {} seconds, please email reopt@nrel.gov for support"\
                    .format(timeout))

        if self.error:
            log("ERROR", self.error)
            raise RuntimeError('reopt', self.error)


class REopt(object):

    xpress_model = "REopt_API.mos"

    def __init__(self, paths, year):

        self.paths = paths
        self.year = year

        self.dfm = DatFileManager()
        file_cmd = os.path.join(paths.inputs, "cmd.log")
        file_cmd_bau = os.path.join(paths.inputs, "cmd_bau.log")
        self.output_file = os.path.join(paths.outputs, "REopt_results.json")

        run_command = self.create_run_command(paths.outputs, REopt.xpress_model, self.dfm.DAT,
                                              self.dfm.command_line_args, bau_string='', cmd_file=file_cmd)

        run_command_bau = self.create_run_command(paths.outputs_bau, REopt.xpress_model, self.dfm.DAT_bau,
                                                  self.dfm.command_line_args_bau, bau_string='Base',
                                                  cmd_file=file_cmd_bau)

        log("INFO", "Initializing Command")
        self.command = Command(run_command)
        log("INFO", "Initializing Command BAU")
        self.command_bau = Command(run_command_bau)

    def run(self, timeout):

        output_dict = dict()

        log("INFO", "Running Command")
        self.command.run(timeout)

        log("INFO", "Running BAU")
        self.command_bau.run(timeout)

        output_dict = self.parse_run_outputs()
        return output_dict

    def create_run_command(self, path_output, xpress_model, DATs, cmd_line_args, bau_string, cmd_file):

        log("DEBUG", "Current Directory: " + os.getcwd())
        log("INFO", "Creating output directory: " + path_output)

        # RE case
        header = 'exec '
        xpress_model_path = os.path.join(self.paths.xpress, xpress_model)

        # Command line constants and Dat file overrides
        outline = ''

        for constant in cmd_line_args:
            outline = ' '.join([outline, constant.strip('\n')])

        for dat_file in DATs:
            if dat_file is not None:
                outline = ' '.join([outline, dat_file.strip('\n')])

        outline.replace('\n', '')

        cmd = r"mosel %s '%s' %s OutputDir='%s' ScenarioPath='%s' BaseString='%s'" \
                 % (header, xpress_model_path, outline, path_output, self.paths.inputs, bau_string)

        log("DEBUG", "Returning Process Command " + cmd)

        # write a cmd file for easy debugging
        with open(cmd_file, 'w') as f:
            f.write(cmd)

        return cmd

    def parse_run_outputs(self):

        if os.path.exists(self.output_file):
            process_results = Results(self.paths.templates, self.paths.outputs, self.paths.outputs_bau,
                                      self.paths.static_outputs, self.year)
            return process_results.get_output()

        else:
            msg = "REopt failed to run. Output file does not exist: " + self.output_file 
            log("DEBUG", "Current directory: " + os.getcwd())
            log("WARNING", msg)
            raise RuntimeError('reopt', msg)
