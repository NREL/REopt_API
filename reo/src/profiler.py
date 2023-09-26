# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
from time import time


"""
Full profiler class implementation which unfortunately is not serializable by Celery
As implemented intended to hold one profile
"""
class Profiler():

    def __init__(self):
        self.start = None
        self.end = None
        self.duration = None

        #assume initialization is invocation
        self.profileStart()

    def profileStart(self):
        self.start = time()

    def profileEnd(self):
        self.end = time()

        if self.start is not None:
            self.duration = self.end - self.start

    def getDuration(self):
        return self.duration




