import json
import os
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat
from unittest import TestCase
from unittest import skip
from reo.models import ModelManager
from reo.utilities import check_common_outputs


class GeneratorSizingTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(GeneratorSizingTests, self).setUp()
        self.reopt_base = '/v1/job/'
        self.test_post = os.path.join('reo', 'tests', 'posts', 'generatorSizingPost.json')

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def outage_tech_to_load(self, list_to_load, outage_start, outage_end):
        """
        To resolve indexing empty list when checking critical_load=generator_to_load,
        define a function that sums up all technologies_to_load and skip if the tech is empty
        @param list_to_load:
        @param outage_start:
        @param outage_end:
        @return:
        """
        tech_to_load = list()
        for tech in list_to_load:
            if tech is not None:
                tech_to_load = [sum_t + t for sum_t, t in zip(tech_to_load, tech[outage_start:outage_end])]
        return tech_to_load

    @skip("Inconsistent value on Red Hat server and other OS")
    def test_generator_sizing_without_existing_diesel_gen(self):
        """
        Test scenario with
        - no existing diesel generator
        - PV and Wind disabled
        - Unlimited max storage
        - generator doesn't sell energy to grid
        - generator is only allowed to operate during outage hours
        """
        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['LoadProfile']['outage_is_major_event'] = True
        nested_data['Scenario']['Site']['PV']['max_kw'] = 0
        nested_data['Scenario']['Site']['Generator']['existing_kw'] = 0
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])

        d_expected = dict()
        d_expected['lcc'] = 236962.0
        d_expected['npv'] = -7685.0
        d_expected['pv_kw'] = 0.0
        d_expected['batt_kw'] = 0.0
        d_expected['batt_kwh'] = 0.0
        d_expected['gen_kw'] = 11.2938
        d_expected['fuel_used_gal'] = 1.52
        d_expected['avoided_outage_costs_us_dollars'] = 1449.55 #1465.83
        d_expected['microgrid_upgrade_cost_us_dollars'] = 2046.6

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise

        critical_load = d['outputs']['Scenario']['Site']['LoadProfile']['critical_load_series_kw']
        generator_to_load = d['outputs']['Scenario']['Site']['Generator']['year_one_to_load_series_kw']
        storage_to_load = d['outputs']['Scenario']['Site']['Storage']['year_one_to_load_series_kw']
        outage_start = d['inputs']['Scenario']['Site']['LoadProfile']['outage_start_hour']
        outage_end = d['inputs']['Scenario']['Site']['LoadProfile']['outage_end_hour']

        # critical load during outage is served by both generator and storage
        list_to_load = [generator_to_load, storage_to_load]
        tech_to_load = self.outage_tech_to_load(list_to_load, outage_start, outage_end)
        for x, y in zip(critical_load[outage_start:outage_end], tech_to_load):
            self.assertAlmostEquals(x, y, places=3)

    def test_generator_sizing_with_existing_diesel_gen(self):
        """
        Test scenario with
        - 100 kW existing diesel generator
        - PV and Wind disabled
        - Unlimited max storage
        - generator doesn't sell energy to grid
        - generator is only allowed to operate during outage hours
        """
        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['LoadProfile']['outage_is_major_event'] = True
        nested_data['Scenario']['Site']['PV']['max_kw'] = 0
        nested_data['Scenario']['Site']['Generator']['existing_kw'] = 100
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])

        d_expected = dict()
        d_expected['lcc'] = 236514.0
        d_expected['npv'] = 0.0
        d_expected['pv_kw'] = 0.0
        d_expected['batt_kw'] = 0.0
        d_expected['batt_kwh'] = 0.0
        d_expected['gen_kw'] = 100.0
        d_expected['fuel_used_gal'] = 1.53
        d_expected['avoided_outage_costs_us_dollars'] = 196470.6
        d_expected['microgrid_upgrade_cost_us_dollars'] = 0.0

        #d_alt_expected catches case where http://www.afanalytics.com/api/climatezone/ is down and we fall back on the nearest city lookup 
        d_alt_expected = dict()
        d_alt_expected['lcc'] = 267216.0
        d_alt_expected['npv'] = 0.0
        d_alt_expected['pv_kw'] = 0.0
        d_alt_expected['batt_kw'] = 0.0
        d_alt_expected['batt_kwh'] = 0.0
        d_alt_expected['gen_kw'] = 100.0
        d_alt_expected['fuel_used_gal'] = 1.32
        d_alt_expected['avoided_outage_costs_us_dollars'] = 204747.97
        d_alt_expected['microgrid_upgrade_cost_us_dollars'] = 0.0

        try:
            check_common_outputs(self, c, d_expected)
        except:
            try:
                check_common_outputs(self, c, d_alt_expected)
            except:
                print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
                print("Error message: {}".format(d['messages']))
                raise

        critical_load = d['outputs']['Scenario']['Site']['LoadProfile']['critical_load_series_kw']
        generator_to_load = d['outputs']['Scenario']['Site']['Generator']['year_one_to_load_series_kw']
        storage_to_load = d['outputs']['Scenario']['Site']['Storage']['year_one_to_load_series_kw']
        outage_start = d['inputs']['Scenario']['Site']['LoadProfile']['outage_start_hour']
        outage_end = d['inputs']['Scenario']['Site']['LoadProfile']['outage_end_hour']

        list_to_load = [generator_to_load, storage_to_load]
        tech_to_load = self.outage_tech_to_load(list_to_load, outage_start, outage_end)
        for x, y in zip(critical_load[outage_start:outage_end], tech_to_load):
            self.assertAlmostEquals(x, y, places=3)

    def test_generator_sizing_with_existing_pv(self):
        """
        Test scenario with
        - no existing diesel generator
        - existing PV considered
        - new PV and Wind disabled
        - Unlimited max storage
        - generator doesn't sell energy to grid
        - generator is only allowed to operate during outage hours
        """
        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['LoadProfile']['outage_is_major_event'] = True
        nested_data['Scenario']['Site']['PV']['max_kw'] = 0
        nested_data['Scenario']['Site']['Generator']['existing_kw'] = 0
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 100
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])

        d_expected = dict()
        d_expected['lcc'] = 244743.0
        d_expected['npv'] = -3959.0
        d_expected['pv_kw'] = 100.0
        d_expected['batt_kw'] = 0.0
        d_expected['batt_kwh'] = 0.0
        d_expected['gen_kw'] = 5.85713
        d_expected['fuel_used_gal'] = 0.79
        d_expected['avoided_outage_costs_us_dollars'] = 2982.63
        d_expected['microgrid_upgrade_cost_us_dollars'] = 1054.2
        d_expected['gen_total_variable_om_cost_us_dollars'] = 1.0
        d_expected['existing_pv_om_cost_us_dollars'] = 11507.0
        d_expected['net_capital_costs_plus_om'] = 15443.0

        #d_alt_expected catches case where http://www.afanalytics.com/api/climatezone/ is down and we fall back on the nearest city lookup 
        d_alt_expected = dict()
        d_alt_expected['lcc'] = 274333.0
        d_alt_expected['npv'] = -2841.0
        d_alt_expected['pv_kw'] = 100.0
        d_alt_expected['batt_kw'] = 0.0
        d_alt_expected['batt_kwh'] = 0.0
        d_alt_expected['gen_kw'] = 4.20221
        d_alt_expected['fuel_used_gal'] = 0.59
        d_alt_expected['avoided_outage_costs_us_dollars'] = 2231.95
        d_alt_expected['microgrid_upgrade_cost_us_dollars'] = 756.3

        try:
            check_common_outputs(self, c, d_expected)
        except:
            try:
                check_common_outputs(self, c, d_alt_expected)
            except:
                print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
                print("Error message: {}".format(d['messages']))
                raise

        critical_load = d['outputs']['Scenario']['Site']['LoadProfile']['critical_load_series_kw']
        generator_to_load = d['outputs']['Scenario']['Site']['Generator']['year_one_to_load_series_kw']
        storage_to_load = d['outputs']['Scenario']['Site']['Storage']['year_one_to_load_series_kw']
        pv_to_load = d['outputs']['Scenario']['Site']['PV']['year_one_to_load_series_kw']
        outage_start = d['inputs']['Scenario']['Site']['LoadProfile']['outage_start_hour']
        outage_end = d['inputs']['Scenario']['Site']['LoadProfile']['outage_end_hour']

        list_to_load = [generator_to_load, storage_to_load, pv_to_load]
        tech_to_load = self.outage_tech_to_load(list_to_load, outage_start, outage_end)
        for x, y in zip(critical_load[outage_start:outage_end], tech_to_load):
            self.assertAlmostEquals(x, y, places=3)

    def test_generator_sizing_with_existing_diesel_gen_and_pv(self):
        """
        Test scenario with
        - 50 kW existing diesel generator
        - 50 kW existing PV
        - New PV and Wind disabled
        - Unlimited max storage
        - generator doesn't sell energy to grid
        - generator is only allowed to operate during outage hours
        """
        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data['Scenario']['Site']['LoadProfile']['outage_is_major_event'] = True
        nested_data['Scenario']['Site']['PV']['max_kw'] = 0
        nested_data['Scenario']['Site']['Generator']['existing_kw'] = 50
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 50
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])

        d_expected = dict()
        d_expected['lcc'] = 238661.0
        d_expected['npv'] = 0.0
        d_expected['pv_kw'] = 50.0
        d_expected['batt_kw'] = 0.0
        d_expected['batt_kwh'] = 0.0
        d_expected['gen_kw'] = 50.0
        d_expected['fuel_used_gal'] = 1.16
        d_expected['avoided_outage_costs_us_dollars'] = 309552.85
        d_expected['microgrid_upgrade_cost_us_dollars'] = 0.0
        d_expected['gen_total_variable_om_cost_us_dollars'] = 1.0
        d_expected['existing_pv_om_cost_us_dollars'] = 5754.0
        d_expected['net_capital_costs_plus_om'] = 9350.0

        #d_alt_expected catches case where http://www.afanalytics.com/api/climatezone/ is down and we fall back on the nearest city lookup 
        d_alt_expected = dict()
        d_alt_expected['lcc'] = 269363.0
        d_alt_expected['npv'] = 0.0
        d_alt_expected['pv_kw'] = 50.0
        d_alt_expected['batt_kw'] = 0.0
        d_alt_expected['batt_kwh'] = 0.0
        d_alt_expected['gen_kw'] = 50.0
        d_alt_expected['fuel_used_gal'] = 0.95
        d_alt_expected['avoided_outage_costs_us_dollars'] = 308097.57
        d_alt_expected['microgrid_upgrade_cost_us_dollars'] = 0.0

        try:
            check_common_outputs(self, c, d_expected)
        except:
            try:
                check_common_outputs(self, c, d_alt_expected)
            except:
                print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
                print("Error message: {}".format(d['messages']))
                raise


        critical_load = d['outputs']['Scenario']['Site']['LoadProfile']['critical_load_series_kw']
        generator_to_load = d['outputs']['Scenario']['Site']['Generator']['year_one_to_load_series_kw']
        storage_to_load = d['outputs']['Scenario']['Site']['Storage']['year_one_to_load_series_kw']
        pv_to_load = d['outputs']['Scenario']['Site']['PV']['year_one_to_load_series_kw']
        outage_start = d['inputs']['Scenario']['Site']['LoadProfile']['outage_start_hour']
        outage_end = d['inputs']['Scenario']['Site']['LoadProfile']['outage_end_hour']

        # when both existing gen and pv are present, the critical load during outage is
        # served by generator + pv + storage
        list_to_load = [generator_to_load, storage_to_load, pv_to_load]
        tech_to_load = self.outage_tech_to_load(list_to_load, outage_start, outage_end)
        # may have to disable this check if the generator is charging battery during the outage hours
        for x, y in zip(critical_load[outage_start:outage_end], tech_to_load):
            self.assertAlmostEquals(x, y, places=3)
