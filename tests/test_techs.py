import json
import os
import shutil
import unittest

from reo.src.dat_file_manager import DatFileManager
from reo.src.techs import PV, Util

temp_folder = os.path.join('tmp', 'test_techs_outputs')
n_timesteps = 8760


class TestTechs(unittest.TestCase):

    def setUp(self):
        self.dfm = DatFileManager(run_id=123, inputs_path=temp_folder)

        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)
        self.dfm.n_timesteps = n_timesteps

        post = json.load(open(os.path.join('tests', 'POST.json'), 'r'))
        self.pv = PV(offline=True, **post)
        self.dfm.add_pv(self.pv)
        self.util = Util(**post)
        self.dfm.add_util(self.util)

        self.dfm.finalize()

    def tearDown(self):
        shutil.rmtree(temp_folder)

    @unittest.skip("test_techs needs updated for expanded DFM")
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
