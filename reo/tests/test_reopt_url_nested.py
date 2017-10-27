import json
import copy
import pickle
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.validators import ValidateNestedInput
from reo.nested_inputs import nested_input_definitions
from reo.validators import ValidateNestedInput
from unittest import skip


class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    REopt_tol = 1e-2

    def setUp(self):
        super(EntryResourceTest, self).setUp()

        self.data_definitions = nested_input_definitions

        self.reopt_base = '/api/v1/reopt/'

        self.missing_rate_urdb = pickle.load(open('reo/tests/missing_rate.p','rb'))
        self.missing_schedule_urdb = pickle.load(open('reo/tests/missing_schedule.p','rb'))

    @property
    def complete_valid_nestedpost(self):
        return json.load(open('reo/tests/nestedPOST.json'))

    def make_url(self,string):
        return self.reopt_base + string

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def check_data_error_response(self, data, text):
        response = self.get_response(data)
        self.assertTrue(text in response.content)

    def test_required(self):

        required = ['latitude','longitude']

        for r in required:
            test_case = self.complete_valid_nestedpost
            del test_case['Scenario']['Site'][r]
            response = self.get_response(test_case)
            text = "Missing Required for Scenario>Site: " + r
            self.assertTrue(text in str(json.loads(response.content)['messages']['errors']['input_errors']))

        electric_tarrif_cases = [['urdb_response','blended_monthly_rates_us_dollars_per_kwh','monthly_demand_charges_us_dollars_per_kw'],['urdb_response','monthly_demand_charges_us_dollars_per_kw'],['urdb_response','blended_monthly_rates_us_dollars_per_kwh']]
        for c in electric_tarrif_cases:
            test_case = self.complete_valid_nestedpost
            for r in c:
                del test_case['Scenario']['Site']['ElectricTariff'][r]
            response = self.get_response(test_case)
            text = "Missing Required for Scenario>Site>ElectricTariff"
            self.assertTrue(text in str(json.loads(response.content)['messages']['errors']['input_errors']))

        load_profile_cases = [['doe_reference_name','annual_kwh','monthly_totals_kwh','loads_kw'],['loads_kw','monthly_totals_kwh','annual_kwh'],  ['loads_kw','doe_reference_name','annual_kwh']]
        for c in load_profile_cases:
            test_case = self.complete_valid_nestedpost
            for r in c:
                del test_case['Scenario']['Site']['LoadProfile'][r]
            response = self.get_response(test_case)
            text = "Missing Required for Scenario>Site>LoadProfile"
            self.assertTrue(text in str(json.loads(response.content)['messages']['errors']['input_errors']))

    def test_valid_data_types(self):

        input = ValidateNestedInput(self.complete_valid_nestedpost, nested=True)

        for attribute, test_data in input.test_data('type'):

            response = self.get_response(test_data)
            text = "Could not convert " + attribute

            self.assertTrue(text in str(json.loads(response.content)['messages']['errors']['input_errors']))
            self.assertTrue("(OOPS)" in str(json.loads(response.content)['messages']['errors']['input_errors']))

    def test_valid_data_ranges(self):

        input = ValidateNestedInput(self.complete_valid_nestedpost, nested=True)

        for attribute, test_data in input.test_data('min'):
            text = "exceeds allowable min"
            response = self.get_response(test_data)
            t = json.loads(response.content)
            self.assertTrue(text in str(json.loads(response.content)['messages']['errors']['input_errors']))

        for attribute, test_data in input.test_data('max'):
                text = "exceeds allowable max"
                response = self.get_response(test_data)
                self.assertTrue(text in str(json.loads(response.content)['messages']['errors']['input_errors']))

        for attribute, test_data in input.test_data('restrict_to'):
            text = "not in allowable inputs"
            response = self.get_response(test_data)
            self.assertTrue(text in str(json.loads(response.content)['messages']['errors']['input_errors']))
    
    def test_urdb_rate(self):

        data =  self.complete_valid_nestedpost

        data['Scenario']['Site']['ElectricTariff']['urdb_response'] =self.missing_rate_urdb
        text = "Missing rate/sell/adj attributes for tier 0 in rate 0 energyratestructure"
        self.check_data_error_response(data,text)

        data['Scenario']['Site']['ElectricTariff']['urdb_response']=self.missing_schedule_urdb

        text = 'energyweekdayschedule contains value 1 which has no associated rate in energyratestructure'
        self.check_data_error_response(data,text)

        text = 'energyweekendschedule contains value 1 which has no associated rate in energyratestructure'
        self.check_data_error_response(data,text)

    def check_common_outputs(self, d_calculated, d_expected):

        c = d_calculated
        e = d_expected

        # check all calculated keys against the expected
        for key, value in e.iteritems():
            tolerance = self.REopt_tol
            if key == 'npv':
                tolerance = 2 * self.REopt_tol

            if key in c:
                self.assertTrue((float(c[key]) - e[key]) / e[key] < tolerance)

        # Total LCC BAU is sum of utility costs
        self.assertTrue((float(c['lcc_bau']) - float(c['total_energy_cost_bau']) - float(c['total_min_charge_adder'])
                         - float(c['total_demand_cost_bau']) - float(c['total_fixed_cost_bau'])) / float(c['lcc_bau']) < self.REopt_tol)

    @skip("Will Fail Until Workflow Complete")
    def test_complex_incentives(self):
        #  Tests scenario where: PV has ITC, federal, state, local rebate with maxes, MACRS, bonus, Battery has ITC, rebate, MACRS, bonus.

        data = {'Scenario': {'user_id': None, 'time_steps_per_hour': None, 'timeout_seconds': None, 'Site': {'LoadProfile': {'annual_kwh': 10000000.0, 'loads_kw': None, 'doe_reference_name': 'RetailStore', 'monthly_totals_kwh': None, 'year': None}, 'critical_load_pct': None, 'Storage': {'total_rebate_us_dollars_per_kw': 100, 'max_kwh': None, 'rectifier_efficiency_pct': None, 'total_itc_pct': None, 'min_kw': None, 'max_kw': None, 'replace_cost_us_dollars_per_kw': None, 'replace_cost_us_dollars_per_kwh': None, 'min_kwh': None, 'installed_cost_us_dollars_per_kw': None, 'battery_replacement_year': None, 'installed_cost_us_dollars_per_kwh': None, 'inverter_efficiency_pct': None, 'canGridCharge': True, 'macrs_bonus_pct': None, 'inverter_replacement_year': None, 'macrs_option_years': 5, 'internal_efficiency_pct': None, 'soc_min_pct': None, 'soc_init_pct': None}, 'land_acres': 1.0, 'latitude': 34.5794343, 'outage_end_hour': None, 'roof_squarefeet': 5000.0, 'PV': {'pbi_years': None, 'macrs_bonus_pct': None, 'max_kw': None, 'pbi_max_us_dollars': None, 'radius': None, 'state_ibi_pct': None, 'utility_rebate_max_us_dollars': None, 'installed_cost_us_dollars_per_kw': None, 'utility_ibi_max_us_dollars': 10000, 'tilt': None, 'gcr': None, 'pbi_system_max_kw': 10, 'utility_ibi_pct': 0.1, 'state_ibi_max_us_dollars': 10000, 'state_rebate_us_dollars_per_kw': 200, 'macrs_option_years': 5, 'state_rebate_max_us_dollars': None, 'dc_ac_ratio': None, 'federal_itc_pct': 0.3, 'degradation_pct': None, 'module_type': 1, 'array_type': 1, 'pbi_us_dollars_per_kwh': 0.0, 'om_cost_us_dollars_per_kw': None, 'utility_rebate_us_dollars_per_kw': 50, 'min_kw': None, 'losses': 0.14, 'federal_rebate_us_dollars_per_kw': 100, 'inv_eff': None, 'azimuth': None}, 'Wind': {'pbi_us_dollars_per_kwh': None, 'installed_cost_us_dollars_per_kw': None, 'macrs_bonus_pct': None, 'om_cost_us_dollars_per_kw': None, 'utility_rebate_us_dollars_per_kw': None, 'min_kw': None, 'pbi_years': None, 'max_kw': None, 'state_rebate_max_us_dollars': None, 'state_rebate_us_dollars_per_kw': None, 'federal_itc_pct': None, 'federal_rebate_us_dollars_per_kw': None, 'pbi_max_us_dollars': None, 'degradation_pct': None, 'pbi_system_max_kw': None, 'macrs_option_years': None, 'state_ibi_pct': None, 'utility_rebate_max_us_dollars': None, 'utility_ibi_pct': None, 'state_ibi_max_us_dollars': None, 'utility_ibi_max_us_dollars': None}, 'Financial': {'om_cost_growth_pct': None, 'escalation_pct': None, 'offtaker_discount_pct': None, 'owner_tax_pct': None, 'analysis_period_years': None, 'offtaker_tax_pct': None, 'owner_discount_pct': None}, 'longitude': -118.1164613, 'ElectricTariff': {'monthly_demand_charges_us_dollars_per_kw': None, 'urdb_response': {'sector': 'Commercial', 'voltageminimum': 2000, 'description': '-Energytieredcharge=generationcharge+deliverycharge\r\n\r\n-Timeofdaydemandcharges(generation-based)aretobeaddedtothemonthlydemandcharge(Deliverybased).', 'peakkwcapacitymax': 200, 'energyattrs': [{'VoltageDiscount(2KV-<50KV)': '$-0.00106/Kwh'}, {'VoltageDiscount(>50KV<220KV)': '$-0.00238/Kwh'}, {'VoltageDiscountat220KV': '$-0.0024/Kwh'}, {'CaliforniaClimatecredit': '$-0.00669/kwh'}], 'enddate': 1451520000, 'peakkwcapacityhistory': 12, 'energyratestructure': [[{'rate': 0.0712, 'unit': 'kWh'}], [{'rate': 0.09368, 'unit': 'kWh'}], [{'rate': 0.066, 'unit': 'kWh'}], [{'rate': 0.08888, 'unit': 'kWh'}], [{'rate': 0.1355, 'unit': 'kWh'}]], 'flatdemandmonths': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'energyweekdayschedule': [[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]], 'energyweekendschedule': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], 'demandweekendschedule': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], 'approved': True, 'utility': 'SouthernCaliforniaEdisonCo', 'flatdemandstructure': [[{'rate': 13.2}]], 'startdate': 1433116800, 'fixedmonthlycharge': 259.2, 'phasewiring': 'SinglePhase', 'name': 'TimeofUse,GeneralService,DemandMetered,OptionB:GS-2TOUB,SinglePhase', 'eiaid': 17609, 'country': 'USA', 'uri': 'http://en.openei.org/apps/IURDB/rate/view/55fc81d7682bea28da64f9ae', 'voltagemaximum': 50000, 'label': '55fc81d7682bea28da64f9ae', 'flatdemandunit': 'kW', 'source': 'http://www.sce.com/NR/sc3/tm2/pdf/ce30-12.pdf', 'voltagecategory': 'Primary', 'peakkwcapacitymin': 20, 'demandattrs': [{'FaciltiesVoltageDiscount(2KV-<50KV)': '$-0.18/KW'}, {'FaciltiesVoltageDiscount>50kV-<220kV': '$-5.78/KW'}, {'FaciltiesVoltageDiscount>220kV': '$-9.96/KW'}, {'TimeVoltageDiscount(2KV-<50KV)': '$-0.70/KW'}, {'TimeVoltageDiscount>50kV-<220kV': '$-1.93/KW'}, {'TimeVoltageDiscount>220kV': '$-1.95/KW'}], 'demandrateunit': 'kW', 'revisions': [1433408708, 1433409358, 1433516188, 1441198316, 1441199318, 1441199417, 1441199824, 1441199996, 1454521683], 'demandratestructure': [[{'rate': 0}], [{'rate': 5.3}], [{'rate': 18.11}]], 'demandweekdayschedule': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]}, 'net_metering_limit_kw': 0, 'blended_monthly_rates_us_dollars_per_kwh': None, 'interconnection_limit_kw': None, 'urdb_rate_name': None, 'wholesale_rate_us_dollars_per_kwh': None, 'urdb_utilty_name': None}, 'outage_start_hour': None}}}

        resp = self.api_client.post(self.url_base, format='json', data=data)
        self.assertHttpCreated(resp)
        d_calculated = json.loads(resp.content)

        d_expected = dict()
        d_expected['lcc'] = 10950029
        d_expected['npv'] = 11276785 - d_expected['lcc']
        d_expected['pv_kw'] = 216.667
        d_expected['batt_kw'] = 106.055
        d_expected['batt_kwh'] = 307.971
        d_expected['year_one_utility_kwh'] = 9621290

        try:
            self.check_common_outputs(d_calculated, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(d_calculated.get('uuid')))
            raise

    @skip("Will Fail Until Workflow Complete")    
    def test_wind(self):
        """
        Validation run for wind scenario that matches REopt desktop results as of 9/26/17.
        Note no tax, no ITC, no MACRS.
        :return:
        """

        wind_post = {'Scenario': {'user_id': None, 'time_steps_per_hour': None, 'timeout_seconds': None, 'Site': {'LoadProfile': {'annual_kwh': 10000000, 'loads_kw': None, 'doe_reference_name': 'MediumOffice', 'monthly_totals_kwh': None, 'year': None}, 'critical_load_pct': None, 'Storage': {'total_rebate_us_dollars_per_kw': None, 'max_kwh': 0, 'rectifier_efficiency_pct': None, 'total_itc_pct': None, 'min_kw': None, 'max_kw': 0, 'replace_cost_us_dollars_per_kw': None, 'replace_cost_us_dollars_per_kwh': None, 'min_kwh': None, 'installed_cost_us_dollars_per_kw': None, 'battery_replacement_year': None, 'installed_cost_us_dollars_per_kwh': None, 'inverter_efficiency_pct': None, 'canGridCharge': None, 'macrs_bonus_pct': None, 'inverter_replacement_year': None, 'macrs_option_years': None, 'internal_efficiency_pct': None, 'soc_min_pct': None, 'soc_init_pct': None}, 'land_acres': None, 'latitude': 39.91065, 'outage_end_hour': None, 'roof_squarefeet': None, 'PV': {'pbi_years': None, 'macrs_bonus_pct': None, 'max_kw': 0, 'pbi_max_us_dollars': None, 'radius': None, 'state_ibi_pct': None, 'utility_rebate_max_us_dollars': None, 'installed_cost_us_dollars_per_kw': None, 'utility_ibi_max_us_dollars': None, 'tilt': None, 'gcr': None, 'pbi_system_max_kw': None, 'utility_ibi_pct': None, 'state_ibi_max_us_dollars': None, 'state_rebate_us_dollars_per_kw': None, 'macrs_option_years': None, 'state_rebate_max_us_dollars': None, 'dc_ac_ratio': None, 'federal_itc_pct': None, 'degradation_pct': None, 'module_type': None, 'array_type': None, 'pbi_us_dollars_per_kwh': None, 'om_cost_us_dollars_per_kw': None, 'utility_rebate_us_dollars_per_kw': None, 'min_kw': None, 'losses': None, 'federal_rebate_us_dollars_per_kw': None, 'inv_eff': None, 'azimuth': None}, 'Wind': {'pbi_us_dollars_per_kwh': None, 'installed_cost_us_dollars_per_kw': None, 'macrs_bonus_pct': 0.0, 'om_cost_us_dollars_per_kw': None, 'utility_rebate_us_dollars_per_kw': None, 'min_kw': None, 'pbi_years': None, 'max_kw': 10000, 'state_rebate_max_us_dollars': None, 'state_rebate_us_dollars_per_kw': None, 'federal_itc_pct': 0, 'federal_rebate_us_dollars_per_kw': None, 'pbi_max_us_dollars': None, 'degradation_pct': None, 'pbi_system_max_kw': None, 'macrs_option_years': 0, 'state_ibi_pct': None, 'utility_rebate_max_us_dollars': None, 'utility_ibi_pct': None, 'state_ibi_max_us_dollars': None, 'utility_ibi_max_us_dollars': None}, 'Financial': {'om_cost_growth_pct': 0.001, 'escalation_pct': 0.006, 'offtaker_discount_pct': 0.07, 'owner_tax_pct': None, 'analysis_period_years': 25, 'offtaker_tax_pct': 0.0, 'owner_discount_pct': None}, 'longitude': -105.2348, 'ElectricTariff': {'monthly_demand_charges_us_dollars_per_kw': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'urdb_response': None, 'net_metering_limit_kw': 1000000.0, 'blended_monthly_rates_us_dollars_per_kwh': [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2], 'interconnection_limit_kw': None, 'urdb_rate_name': None, 'wholesale_rate_us_dollars_per_kwh': None, 'urdb_utilty_name': None}, 'outage_start_hour': None}}}

        d_expected = dict()
        d_expected['lcc'] = 9849424
        d_expected['npv'] = 14861356
        d_expected['wind_kw'] = 4077.9
        d_expected['average_annual_energy_exported_wind'] = 5751360
        d_expected['net_capital_costs_plus_om'] = 9835212

        resp = self.api_client.post(self.url_base, format='json', data=wind_post)
        self.assertHttpCreated(resp)
        d_calculated = json.loads(resp.content)

        self.check_common_outputs(d_calculated, d_expected)
        
    @skip("Will Fail Until Workflow Complete")
    def test_valid_nested_posts(self):

    #Can't test until we work through new workflow
        swaps = [['urdb_rate'], ['demand_charge', 'blended_utility_rate']]
        null = None
        data = {"losses":null,"roof_area":5000.0,"owner_tax_rate":null,"pv_itc_federal":null,"batt_can_gridcharge":True,"load_profile_name":"RetailStore","batt_replacement_cost_kwh":null,"pv_rebate_state_max":null,"pv_rebate_utility":null,"pv_ibi_utility":null,"pv_rebate_federal":null,"analysis_period":null,"pv_rebate_state":null,"offtaker_tax_rate":null,"pv_macrs_schedule":5,"pv_kw_max":null,"load_size":10000000.0,"tilt":null,"batt_kwh_max":null,"pv_rebate_federal_max":null,"batt_replacement_cost_kw":null,"batt_rebate_total":null,"longitude":-118.1164613,"pv_ibi_state":null,"batt_kw_max":null,"pv_pbi":null,"batt_inverter_efficiency":null,"offtaker_discount_rate":null,"batt_efficiency":null,"batt_soc_min":null,"batt_macrs_schedule":5,"batt_replacement_year_kwh":null,"latitude":34.5794343,"owner_discount_rate":null,"batt_replacement_year_kw":null,"module_type":1,"batt_kw_min":null,"array_type":1,"rate_escalation":null,"batt_cost_kw":null,"pv_kw_min":null,"pv_pbi_max":null,"pv_pbi_years":null,"land_area":1.0,"dc_ac_ratio":null,"net_metering_limit":null,"batt_itc_total":null,"azimuth":null,"batt_soc_init":null,"pv_rebate_utility_max":null,"pv_ibi_utility_max":null,"pv_itc_federal_max":null,"urdb_rate":{"sector":"Commercial","peakkwcapacitymax":200,"energyweekdayschedule":[[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[2,2,2,2,2,2,2,2,3,3,3,3,4,4,4,4,4,4,3,3,3,3,3,2],[2,2,2,2,2,2,2,2,3,3,3,3,4,4,4,4,4,4,3,3,3,3,3,2],[2,2,2,2,2,2,2,2,3,3,3,3,4,4,4,4,4,4,3,3,3,3,3,2],[2,2,2,2,2,2,2,2,3,3,3,3,4,4,4,4,4,4,3,3,3,3,3,2],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0]],"demandattrs":[{"Facilties Voltage Discount (2KV-<50KV)":"$-0.18/KW"},{"Facilties Voltage Discount >50 kV-<220kV":"$-5.78/KW"},{"Facilties Voltage Discount >220 kV":"$-9.96/KW"},{"Time Voltage Discount (2KV-<50KV)":"$-0.70/KW"},{"Time Voltage Discount >50 kV-<220kV":"$-1.93/KW"},{"Time Voltage Discount >220 kV":"$-1.95/KW"}],"energyratestructure":[[{"rate":0.0712,"unit":"kWh"}],[{"rate":0.09368,"unit":"kWh"}],[{"rate":0.066,"unit":"kWh"}],[{"rate":0.08888,"unit":"kWh"}],[{"rate":0.1355,"unit":"kWh"}]],"energyweekendschedule":[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],"demandweekendschedule":[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],"utility":"Southern California Edison Co","flatdemandstructure":[[{"rate":13.2}]],"startdate":1433116800,"phasewiring":"Single Phase","source":"http://www.sce.com/NR/sc3/tm2/pdf/ce30-12.pdf","label":"55fc81d7682bea28da64f9ae","flatdemandunit":"kW","eiaid":17609,"voltagecategory":"Primary","revisions":[1433408708,1433409358,1433516188,1441198316,1441199318,1441199417,1441199824,1441199996,1454521683],"demandweekdayschedule":[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,0],[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,0],[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,0],[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],"voltageminimum":2000,"description":"- Energy tiered charge = generation charge + delivery charge\r\n\r\n- Time of day demand charges (generation-based) are to be added to the monthly demand charge(Delivery based).","energyattrs":[{"Voltage Discount (2KV-<50KV)":"$-0.00106/Kwh"},{"Voltage Discount (>50 KV<220 KV)":"$-0.00238/Kwh"},{"Voltage Discount at 220 KV":"$-0.0024/Kwh"},{"California Climate credit":"$-0.00669/kwh"}],"demandrateunit":"kW","flatdemandmonths":[0,0,0,0,0,0,0,0,0,0,0,0],"approved":True,"fixedmonthlycharge":259.2,"enddate":1451520000,"name":"Time of Use, General Service, Demand Metered, Option B: GS-2 TOU B, Single Phase","country":"USA","uri":"http://en.openei.org/apps/IURDB/rate/view/55fc81d7682bea28da64f9ae","voltagemaximum":50000,"peakkwcapacitymin":20,"peakkwcapacityhistory":12,"demandratestructure":[[{"rate":0}],[{"rate":5.3}],[{"rate":18.11}]]},"pv_cost":null,"rate_inflation":null,"batt_kwh_min":null,"pv_ibi_state_max":null,"pv_pbi_system_max":null,"batt_rectifier_efficiency":null,"pv_om":null,"batt_cost_kwh":null,"crit_load_factor":1.0}

        for add in swaps:
           # Test All  Data and  Valid Rate Inputs

            if add == swaps[1]:
                del data['urdb_rate']
                del data['load_size']
                data['load_monthly_kwh'] = [100, 200, 250, 300, 350, 350, 400, 400, 350, 250, 250, 200]
                data['blended_utility_rate'] = [i*2 for i in [0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066]]
                data['demand_charge'] = [10.00, 10.00, 10.00, 10.00, 10.00, 10.00, 10.00, 10.00, 10.00, 10.00, 10.00, 10.00]

                data = ValidateNestedInput(data, nested=False).input_dict
                resp = self.api_client.post(self.reopt_base, format='json', data=data)
                self.assertHttpCreated(resp)
                d = json.loads(resp.content)

                npv = 855.0
                lcc = 2998.0
                pv_kw = 1.24622
                batt_kw = 0.163791
                batt_kwh = 0.52211
                yr_one = 1488.5226

                self.assertTrue((float(d['lcc']) - lcc) / lcc < self.REopt_tol)
                self.assertTrue((float(d['npv']) - npv) / npv < self.REopt_tol * 2)  # *2 b/c npv is difference of two outputs
                self.assertTrue((float(d['pv_kw']) - pv_kw) / pv_kw < self.REopt_tol)
                self.assertTrue((float(d['batt_kw']) - batt_kw) / batt_kw < self.REopt_tol)
                self.assertTrue((float(d['batt_kwh']) - batt_kwh) / batt_kwh < self.REopt_tol)
                self.assertTrue((float(d['year_one_utility_kwh']) - yr_one) / yr_one < self.REopt_tol)

            else:
                data = ValidateNestedInput(data, nested=False).input_dict
                resp = self.api_client.post(self.reopt_base, format='json', data=data)
                self.assertHttpCreated(resp)
                d = json.loads(resp.content)

                lcc = 12651213.0
                npv = 385668.0
                pv_kw = 185.798
                batt_kw = 200.866
                batt_kwh = 960.659
                yr_one_kwh = 9709753.5354

                self.assertTrue((float(d['lcc']) -lcc) /lcc  < self.REopt_tol)
                self.assertTrue((float(d['npv']) - npv) / npv < self.REopt_tol * 2)  # *2 b/c npv is difference of two outputs
                self.assertTrue((float(d['pv_kw']) - pv_kw) / pv_kw < self.REopt_tol)
                self.assertTrue((float(d['batt_kw']) - batt_kw) / batt_kw < self.REopt_tol)
                self.assertTrue((float(d['batt_kwh']) - batt_kwh) / batt_kwh < self.REopt_tol)
                self.assertTrue((float(d['year_one_utility_kwh']) - yr_one_kwh) / yr_one_kwh < self.REopt_tol)