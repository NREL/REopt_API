import os
import shutil
from reo.utilities import check_directory_created


class Paths(object):
    """
    object for contain project paths. facilitates passing paths to other objects.
    """
    def __init__(self, run_uuid):

        self.egg = os.getcwd()
        self.templates = os.path.join(self.egg, "Xpress")
        self.xpress = os.path.join(self.egg, "Xpress")
        self.run = os.path.join(self.xpress, "Run" + str(run_uuid))
        self.inputs = os.path.join(self.run, "Inputs")
        self.static_outputs = os.path.join(self.egg, "static", "files", str(run_uuid))

        if os.path.exists(self.run):
            shutil.rmtree(self.run)

        for f in [self.run, self.inputs, self.static_outputs]:
            os.mkdir(f)
            check_directory_created(f)
