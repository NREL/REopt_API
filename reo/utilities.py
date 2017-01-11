import numpy as np
import datetime, time, threading, signal
from subprocess import Popen, PIPE
import psutil
from tastypie.exceptions import ImmediateHttpResponse
from exceptions import SubprocessTimeoutError

from log_levels import log
import logging

def present_worth_factor(years, escalation_rate, discount_rate):
    pwf = 0
    for y in range(1, years+1):
        pwf = pwf + np.power(1+escalation_rate, y)/np.power(1+discount_rate, y)
    return np.around(pwf, 2)

class Command(object):

    def __init__(self, cmd):
        self.cmd = cmd
	self.process = None

    def run(self, timeout):
        def target():
            self.process = Popen(self.cmd)
            self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
            raise ImmediateHttpResponse("Process Timed Out")        
