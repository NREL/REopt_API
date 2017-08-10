import numpy as np
import threading
from subprocess import Popen
from shlex import split
from tastypie.exceptions import ImmediateHttpResponse

from log_levels import log
import os

def present_worth_factor(years, escalation_rate, discount_rate):
    pwf = 0
    for y in range(1, years+1):
        pwf = pwf + np.power(1+escalation_rate, y)/np.power(1+discount_rate, y)
    return np.around(pwf, 2)


def check_directory_created(path):
    if not os.path.exists(path):
        log('ERROR', "Directory: " + path + " failed to create")
        raise ImmediateHttpResponse("Directory failed to create")


def write_var(f, var, dat_var):
    f.write(dat_var + ": [\n")
    if isinstance(var, list):
        for i in var:
            f.write(str(i) + "\n")
    else:
        f.write(str(var) + "\n")
    f.write("]\n")


def write_single_variable(path, var, dat_var, mode='w'):
    log("INFO", "Writing " + dat_var + " to " + path)
    f = open(path, mode)
    write_var(f, var, dat_var)
    f.close()


def is_error(output_dictionary):
    error = False
    [d.lower() for d in output_dictionary]
    if 'error' in output_dictionary:
        error = output_dictionary
    return error


class Command(object):

    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):

        error = False

        def target():
            self.process = Popen(split(self.cmd))
            log("INFO", "XPRESS" + str(self.process.communicate()))
       
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
            error = "REopt optimization exceeded timeout: %s seconds, please email reopt@nrel.gov for support" % (timeout)
        return error
