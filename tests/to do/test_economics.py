import os
from django.test import TestCase
from reo.economics import Economics
import filecmp


class EconomicsTestCase(TestCase):

    economics = []
    file_test = []
    file_base = []

    pv_om = None
    pv_om_default = 20
    batt_replacement_cost_kwh = 3000

    # mimic user passing in info
    def setUp(self):
        self.file_test = os.path.join(os.getcwd(), 'tests', 'economics_test.dat')
        self.file_base = os.path.join('Xpress', 'DatLibrary', 'Economics', 'economics.dat')

    def initialize_economics(self,  inputs, path_name, business_as_usual):

        self.economics = Economics(inputs, path_name, business_as_usual)

    # Does the Economics class initialize correctly
    def test_economics_initialization(self):
        self.initialize_economics(inputs, path_name, business_as_usual)

        batt_replacement_cost_kwh = self.economics.batt_replacement_cost_kwh
        pv_om = self.economics.pv_om

        # should have overwritten default
        self.assertEqual(self.batt_replacement_cost_kwh, batt_replacement_cost_kwh)

        # should have used default
        self.assertEqual(self.pv_om_default, pv_om)

    # Does the economics file get created
    def test_economics_file(self):
        self.assertEqual(os.path.exists(self.file_test), True)

    # Does passing no values result in the correct default file
    def test_base_case(self):
        self.initialize_economics(self.file_test, None, None, None, None, None, None, None, None, None, None, None,
                                  None, None, None, None, None, None, None, None, None, None, None, None)
        self.assertTrue(filecmp.cmp(self.file_base, self.file_test))