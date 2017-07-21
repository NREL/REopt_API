from reo.techs import PV, Util
from reo.dat_file_manager import DatFileManager
import unittest
import json
import os
import shutil

temp_folder = os.path.join('tmp', 'test_techs_outputs')
n_timesteps = 8760


class TestTechs(unittest.TestCase):

    def setUp(self):
        self.dfm = DatFileManager()
        self.dfm.run_id = 123 # dfm is a singleton
        self.dfm.path_inputs = temp_folder
        os.mkdir(temp_folder)
        self.dfm.n_timesteps = n_timesteps

        post = json.load(open(os.path.join('tests', 'POST.json'), 'r'))
        self.pv = PV(**post)
        self.util = Util(**post)

        self.dfm.finalize()

    def tearDown(self):
        shutil.rmtree(temp_folder)

    def test_prod_factor(self):

        prod_factor = list()
        with open(os.path.join(temp_folder, "GIS_" + str(self.dfm.run_id) + ".dat"), 'r') as f:
            for line in f:
                prod_factor.append(line.strip("\t \n ,"))

        self.assertEqual(len(prod_factor), n_timesteps * 12 + 2)

        prod_factor_bau = list()
        with open(os.path.join(temp_folder, "GIS_" + str(self.dfm.run_id) + "_bau.dat"), 'r') as f:
            for line in f:
                prod_factor_bau.append(line.strip("\t \n ,"))

        self.assertEqual(len(prod_factor_bau), n_timesteps * 4 + 2)
