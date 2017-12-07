from __future__ import absolute_import, unicode_literals
import os
import subprocess32 as sp
import sys
import traceback
from shlex import split
from reo.log_levels import log
from celery import shared_task
from reo.exceptions import *


def create_run_command(output_path, paths, xpress_model, DATs, cmd_line_args, bau_string, cmd_file):

    log("DEBUG", "Current Directory: " + os.getcwd())

    # RE case
    header = 'exec '
    xpress_model_path = os.path.join(paths['xpress'], xpress_model)

    # Command line constants and Dat file overrides
    outline = ''

    for constant in cmd_line_args:
        outline = ' '.join([outline, constant.strip('\n')])

    for dat_file in DATs:
        if dat_file is not None:
            outline = ' '.join([outline, dat_file.strip('\n')])

    outline.replace('\n', '')

    cmd = r"mosel %s '%s' %s OutputDir='%s' ScenarioPath='%s' BaseString='%s'" \
             % (header, xpress_model_path, outline, output_path, paths['inputs'], bau_string)

    log("DEBUG", "Returning Process Command " + cmd)

    # write a cmd file for easy debugging
    with open(cmd_file, 'w') as f:
        f.write(cmd)

    return cmd


@shared_task(bind=True, base=TaskExceptionHandler)
def reopt(self, dfm, paths, data, bau=False):

    self.name = 'reopt'
    self.data = data

    timeout = data['inputs']['Scenario']['timeout_seconds']
    xpress_model = "REopt_API.mos"

    file_cmd = os.path.join(paths['inputs'], "cmd.log")
    file_cmd_bau = os.path.join(paths['inputs'], "cmd_bau.log")

    if bau:
        output_path = paths['outputs_bau']
        run_command = create_run_command(output_path, paths, xpress_model, dfm['DAT_bau'],
                                         dfm['command_line_args_bau'], bau_string='Base',
                                         cmd_file=file_cmd_bau)
    else:
        output_path = paths['outputs']
        run_command = create_run_command(output_path, paths, xpress_model, dfm['DAT'],
                                         dfm['command_line_args'], bau_string='', cmd_file=file_cmd)

    log("INFO", "Running REopt")

    try:
        status = sp.check_output(split(run_command), stderr=sp.STDOUT, timeout=timeout)  # fails if returncode != 0

    except sp.CalledProcessError as e:
        msg = "REopt failed to start. Error code {}.\n{}".format(e.returncode, e.output)
        log("ERROR", msg)
        raise RuntimeError('REopt', msg)

    except sp.TimeoutExpired:
        msg = "Optimization exceeded timeout: {} seconds.".format(timeout)
        log("ERROR", msg)
        exc_traceback = sys.exc_info()[2]
        task = 'reopt' if not bau else 'reopt-bau'
        raise SubprocessTimeout(task=task, message=msg, run_uuid=data['outputs']['Scenario']['run_uuid'],
                                traceback=traceback.format_tb(exc_traceback, limit=1))

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        # raise UnexpectedException(exc_type, exc_value, exc_traceback)

    else:
        log("INFO", "REopt run successfully. Status {}".format(status))

        if status.strip() != 'optimal':
            log("ERROR", "REopt status not optimal. Raising NotOptimal Exception.")
            exc_traceback = sys.exc_info()[2]
            task = 'reopt' if not bau else 'reopt-bau'
            raise NotOptimal(task=task, run_uuid=data['outputs']['Scenario']['run_uuid'],
                             traceback=traceback.format_tb(exc_traceback, limit=1), status=status.strip())

"""
NOTE: Python 3 introduced Exception chaining using `from` statements, but we are using Python 2 :(
"""