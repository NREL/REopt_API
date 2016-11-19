import numpy as np
import subprocess,threading,datetime
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
	self.process = None

    def timeout( p ):
        if p.poll() is None:
            try:
                p.kill()
                print 'Error: process taking too long to complete--terminating'
            except OSError as e:
                if e.errno != errno.ESRCH:
                    raise

    def run(self,to):   
        p  = subprocess.Popen(self.cmd, shell=True,universal_newlines=True,
            	stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print self.cmd
        t = threading.Timer(10.0, to, [p])
        t.start()
	t.join()   
