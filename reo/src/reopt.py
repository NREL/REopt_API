import os
import subprocess32 as sp
from shlex import split
from reo.log_levels import log
from reo.results import Results


class Command(object):

    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.error = False

    def run(self, timeout):

        try:
            status = sp.check_output(split(self.cmd), stderr=sp.STDOUT, timeout=timeout)  # fails if returncode != 0

        except sp.CalledProcessError as e:
            msg = "REopt failed to start. Error code {}.\n{}".format(e.returncode, e.output)
            log("ERROR", msg)
            raise RuntimeError('REopt', msg)

        except sp.TimeoutExpired:
            raise RuntimeError('REopt', "Optimization exceeded timeout: {} seconds, please email reopt@nrel.gov \
                                         for support".format(timeout))
        log("INFO", "REopt run successfully. Status {}".format(status))

        if status.strip() != 'optimal':
            raise RuntimeError('REopt', "Could not find an optimal solution for these inputs.")


class REopt(object):

    xpress_model = "REopt_API.mos"

    def __init__(self, dfm, paths, year):

        self.paths = paths
        self.year = year

        self.dfm = dfm
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

        log("INFO", "Running Command")
        self.command.run(timeout)

        log("INFO", "Running BAU")
        self.command_bau.run(timeout)

        output_dict = self.parse_run_outputs()
        return output_dict

    def create_run_command(self, path_output, xpress_model, DATs, cmd_line_args, bau_string, cmd_file):

        log("DEBUG", "Current Directory: " + os.getcwd())

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
            msg = "Optimization failed to run. Output file does not exist: " + self.output_file
            log("DEBUG", "Current directory: " + os.getcwd())
            log("WARNING", msg)
            raise RuntimeError('REopt', msg)
