import numpy as np
import datetime, time, threading, signal
from subprocess import Popen, PIPE
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


class Command(object):

    def __init__(self, cmd):
        self.cmd = cmd
	self.process = None

    def run(self, timeout):
        def target():
            #from IPython import embed
            #embed()
            self.process = Popen(self.cmd)
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
            raise ImmediateHttpResponse("Process Timed Out")        
