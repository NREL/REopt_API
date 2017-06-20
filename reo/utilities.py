import numpy as np
import datetime, time, threading, signal
from subprocess import Popen, PIPE
from shlex import split
import psutil
from tastypie.exceptions import ImmediateHttpResponse
from exceptions import SubprocessTimeoutError

from log_levels import log
import logging
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
            f.write(str(i) + "\t,\n")
    else:
        f.write(str(var) + "\t,\n")
    f.write("]\n")


def write_single_variable(path, var, dat_var, mode='w'):
    log("INFO", "Writing " + dat_var + " to " + path)
    f = open(path, mode)
    write_var(f, var, dat_var)
    f.close()


class Command(object):

    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
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
            return "Process Exceeeded Timeout: %s seconds" % (timeout)
        return True
