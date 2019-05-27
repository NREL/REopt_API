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

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    @skip("Yet to benckmark with REopt Desktop")
    def test_generator_sizing_without_existing_diesel_gen(self):
        """
        Test scenario with
        - no existing diesel generator
        - PV and Wind disabled
        - Unlimited max storage
        - generator doesn't sell energy to grid
        - generator is only allowed to operate during outage hours
        .
        :return:
        """
        test_post = os.path.join('reo', 'tests', 'generatorSizingPost.json')
        nested_data = json.load(open(test_post, 'rb'))
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
        d_expected['lcc'] = "get from REopt Desktop"
        d_expected['npv'] = "get from REopt Desktop"
        d_expected['pv_kw'] = "get from REopt Desktop"
        d_expected['batt_kw'] = "get from REopt Desktop"
        d_expected['batt_kwh'] = "get from REopt Desktop"
        d_expected['fuel_used_gal'] = "get from REopt Desktop"
        d_expected['avoided_outage_costs_us_dollars'] = "get from REopt Desktop"
        d_expected['microgrid_upgrade_cost_us_dollars'] = "get from REopt Desktop"

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise

        critical_load = d['outputs']['Scenario']['Site']['LoadProfile']['critical_load_series_kw']
        generator_to_load = d['outputs']['Scenario']['Site']['Generator']['year_one_to_load_series_kw']
        outage_start = d['inputs']['Scenario']['Site']['LoadProfile']['outage_start_hour']
        outage_end = d['inputs']['Scenario']['Site']['LoadProfile']['outage_end_hour']

        for x, y in zip(critical_load[outage_start:outage_end], generator_to_load[outage_start:outage_end]):
            self.assertAlmostEquals(x, y, places=3)


    @skip("Yet to benckmark with REopt Desktop")
    def test_generator_sizing_with_existing_diesel_gen(self):
        """
        Test scenario with
        - 100 kW existing diesel generator
        - PV and Wind disabled
        - Unlimited max storage
        - generator doesn't sell energy to grid
        - generator is only allowed to operate during outage hours
        .
        :return:
        """
        test_post = os.path.join('reo', 'tests', 'generatorSizingPost.json')
        nested_data = json.load(open(test_post, 'rb'))
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
        d_expected['lcc'] = "get from REopt Desktop"
        d_expected['npv'] = "get from REopt Desktop"
        d_expected['pv_kw'] = "get from REopt Desktop"
        d_expected['batt_kw'] = "get from REopt Desktop"
        d_expected['batt_kwh'] = "get from REopt Desktop"
        d_expected['fuel_used_gal'] = "get from REopt Desktop"
        d_expected['avoided_outage_costs_us_dollars'] = "get from REopt Desktop"
        d_expected['microgrid_upgrade_cost_us_dollars'] = "get from REopt Desktop"

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise

        critical_load = d['outputs']['Scenario']['Site']['LoadProfile']['critical_load_series_kw']
        generator_to_load = d['outputs']['Scenario']['Site']['Generator']['year_one_to_load_series_kw']
        outage_start = d['inputs']['Scenario']['Site']['LoadProfile']['outage_start_hour']
        outage_end = d['inputs']['Scenario']['Site']['LoadProfile']['outage_end_hour']

        # may have to disable this check if the generator is charging battery during the outage hours
        for x, y in zip(critical_load[outage_start:outage_end], generator_to_load[outage_start:outage_end]):
            self.assertAlmostEquals(x, y, places=3)



    @skip("Yet to benckmark with REopt Desktop")
    def test_generator_sizing_with_existing_pv(self):
        """
        Test scenario with
        - no existing diesel generator
        - existing PV considered
        - new PV and Wind disabled
        - Unlimited max storage
        - generator doesn't sell energy to grid
        - generator is only allowed to operate during outage hours
        .
        :return:
        """
        test_post = os.path.join('reo', 'tests', 'generatorSizingPost.json')
        nested_data = json.load(open(test_post, 'rb'))
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
        d_expected['lcc'] = "get from REopt Desktop"
        d_expected['npv'] = "get from REopt Desktop"
        d_expected['pv_kw'] = "get from REopt Desktop"
        d_expected['batt_kw'] = "get from REopt Desktop"
        d_expected['batt_kwh'] = "get from REopt Desktop"
        d_expected['fuel_used_gal'] = "get from REopt Desktop"
        d_expected['avoided_outage_costs_us_dollars'] = "get from REopt Desktop"
        d_expected['microgrid_upgrade_cost_us_dollars'] = "get from REopt Desktop"
        d_expected['existing_gen_om_cost_us_dollars'] = "get from REopt Desktop"
        d_expected['existing_pv_om_cost_us_dollars'] = "get from REopt Desktop"
        d_expected['net_capital_costs_plus_om_us_dollars_bau'] = "get from REopt Desktop"

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise

        critical_load = d['outputs']['Scenario']['Site']['LoadProfile']['critical_load_series_kw']
        generator_to_load = d['outputs']['Scenario']['Site']['Generator']['year_one_to_load_series_kw']
        outage_start = d['inputs']['Scenario']['Site']['LoadProfile']['outage_start_hour']
        outage_end = d['inputs']['Scenario']['Site']['LoadProfile']['outage_end_hour']

        for x, y in zip(critical_load[outage_start:outage_end], generator_to_load[outage_start:outage_end]):
            self.assertAlmostEquals(x, y, places=3)


    @skip("Yet to benckmark with REopt Desktop")
    def test_generator_sizing_with_existing_diesel_gen_and_pv(self):
        """
        Test scenario with
        - 50 kW existing diesel generator
        - 50 kW existing PV
        - New PV and Wind disabled
        - Unlimited max storage
        - generator doesn't sell energy to grid
        - generator is only allowed to operate during outage hours
        .
        :return:
        """
        test_post = os.path.join('reo', 'tests', 'generatorSizingPost.json')
        nested_data = json.load(open(test_post, 'rb'))
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
        d_expected['lcc'] = "get from REopt Desktop"
        d_expected['npv'] = "get from REopt Desktop"
        d_expected['pv_kw'] = "get from REopt Desktop"
        d_expected['batt_kw'] = "get from REopt Desktop"
        d_expected['batt_kwh'] = "get from REopt Desktop"
        d_expected['fuel_used_gal'] = "get from REopt Desktop"
        d_expected['avoided_outage_costs_us_dollars'] = "get from REopt Desktop"
        d_expected['microgrid_upgrade_cost_us_dollars'] = "get from REopt Desktop"
        d_expected['existing_gen_om_cost_us_dollars'] = "get from REopt Desktop"
        d_expected['existing_pv_om_cost_us_dollars'] = "get from REopt Desktop"
        d_expected['net_capital_costs_plus_om_us_dollars_bau'] = "get from REopt Desktop"

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise

        critical_load = d['outputs']['Scenario']['Site']['LoadProfile']['critical_load_series_kw']
        generator_to_load = d['outputs']['Scenario']['Site']['Generator']['year_one_to_load_series_kw']
        outage_start = d['inputs']['Scenario']['Site']['LoadProfile']['outage_start_hour']
        outage_end = d['inputs']['Scenario']['Site']['LoadProfile']['outage_end_hour']

        # may have to disable this check if the generator is charging battery during the outage hours
        for x, y in zip(critical_load[outage_start:outage_end], generator_to_load[outage_start:outage_end]):
            self.assertAlmostEquals(x, y, places=3)



    @skip("Yet to benckmark with REopt Desktop")
    def test_generator_sizing_when_allowed_to_operatre_year_long(self):
        """
        Test scenario with
        - New PV and Wind disabled
        - Unlimited max storage
        - generator doesn't sell energy to grid
        - generator is allowed to operate for all the hours of the year
        .
        :return:
        """
        test_post = os.path.join('reo', 'tests', 'generatorSizingPost.json')
        nested_data = json.load(open(test_post, 'rb'))
        nested_data['Scenario']['Site']['LoadProfile']['outage_is_major_event'] = True
        nested_data['Scenario']['Site']['PV']['max_kw'] = 0
        nested_data['Scenario']['Site']['Generator']['existing_kw'] = 0
        nested_data['Scenario']['Site']['PV']['existing_kw'] = 0
        nested_data['Scenario']['Site']['PV']['generator_only_runs_during_grid_outage'] = False
        resp = self.get_response(data=nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])

        d_expected = dict()
        d_expected['lcc'] = "get from REopt Desktop"
        d_expected['npv'] = "get from REopt Desktop"
        d_expected['pv_kw'] = "get from REopt Desktop"
        d_expected['batt_kw'] = "get from REopt Desktop"
        d_expected['batt_kwh'] = "get from REopt Desktop"
        d_expected['fuel_used_gal'] = "get from REopt Desktop"
        d_expected['avoided_outage_costs_us_dollars'] = "get from REopt Desktop"
        d_expected['microgrid_upgrade_cost_us_dollars'] = "get from REopt Desktop"
        d_expected['existing_gen_om_cost_us_dollars'] = "get from REopt Desktop"
        d_expected['existing_pv_om_cost_us_dollars'] = "get from REopt Desktop"
        d_expected['net_capital_costs_plus_om_us_dollars_bau'] = "get from REopt Desktop"

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise

        critical_load = d['outputs']['Scenario']['Site']['LoadProfile']['critical_load_series_kw']
        generator_to_load = d['outputs']['Scenario']['Site']['Generator']['year_one_to_load_series_kw']
        outage_start = d['inputs']['Scenario']['Site']['LoadProfile']['outage_start_hour']
        outage_end = d['inputs']['Scenario']['Site']['LoadProfile']['outage_end_hour']

        # may have to disable this check if the generator is charging battery during the outage hours
        for x, y in zip(critical_load[outage_start:outage_end], generator_to_load[outage_start:outage_end]):
            self.assertAlmostEquals(x, y, places=3)