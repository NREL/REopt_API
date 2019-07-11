import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.src.pvwatts import PVWatts


class TestPVWatts(ResourceTestCaseMixin, TestCase):

    def setUp(self):

        self.pvwatts_denver = PVWatts(latitude=39.7392, longitude=-104.99, tilt=40, verify=False)
        #self.pvwatts_zimbabwe = PVWatts(latitude=-19.0154, longitude=29.1549, tilt=20, verify=False)
        #self.pvwatts_southafrica = PVWatts(latitude=-26.2041, longitude=28.0473, tilt=20, verify=False)


    def test_pvwatts(self):

        denver_data = self.pvwatts_denver.data
        self.assertAlmostEqual(denver_data['outputs']['ac_annual'], 1677, places=0)
        self.assertEquals(len(denver_data['outputs']['ac']), 8760)
        self.assertEquals(denver_data['station_info']['solar_resource_file'], 'W10498N3973.csv')
        self.assertEquals(denver_data['station_info']['distance'], 1335)

        #zimbabwe_data = self.pvwatts_zimbabwe.data
        #self.assertAlmostEqual(zimbabwe_data['outputs']['ac_annual'], 1319, places=0)
        #self.assertEquals(len(zimbabwe_data['outputs']['ac']), 8760)

        #sa_data = self.pvwatts_southafrica.data
        #self.assertAlmostEqual(sa_data['outputs']['ac_annual'], 1243, places=0)
        #self.assertEquals(len(sa_data['outputs']['ac']), 8760)