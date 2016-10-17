import numpy as np
import subprocess32
import psutil
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

    def kill(self, proc_pid):
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            proc.kill()
            log('ERROR', 'Killed process %d' % proc.pid)
        process.kill()

    def run(self, timeout):
        proc = subprocess32.Popen(self.cmd)

        try:
            proc.wait(timeout=timeout)
        except subprocess32.TimeoutExpired:
            error_message = 'Initiating killing process %d after timeout of %d seconds' % (proc.pid, int(timeout))
            self.kill(proc.pid)
            log('ERROR', error_message)
            raise SubprocessTimeoutError(error_message)

