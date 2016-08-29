import os
from django.test import TestCase
from reo.economics import Economics


class EconomicsTestCase(TestCase):

    economics = []
    test_file = []

    pv_OM = None
    pv_OM_default = 20
    batt_replacement_kWh = 3000

    # mimic user passing in info
    def setUp(self):

        self.test_file = os.path.join(os.getcwd(), 'tests', 'economics_test.dat')

        if os.path.exists(self.test_file):
            os.remove(self.test_file)

        self.economics = Economics(self.test_file,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   self.batt_replacement_kWh)

    # Does the Economics class initialize correctly
    def test_economics_initialization(self):

        batt_replacement_kWh = self.economics.batt_repl_kWh
        pv_om = self.economics.pv_OM

        # should have overwritten default
        self.assertEqual(self.batt_replacement_kWh, batt_replacement_kWh)

        # should have used default
        self.assertEqual(self.pv_OM_default, pv_om)

    # Does the economics file get created
    def test_economics_file(self):

        self.assertEqual(os.path.exists(self.test_file), True)






