import json
import copy
import pickle
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from reo.validators import ValidateNestedInput


class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    REopt_tol = 1e-2

    def setUp(self):
        super(EntryResourceTest, self).setUp()

        self.data_definitions = ValidateNestedInput({}).web_inputs

        self.reopt_base = '/api/v1/reopt/'

        self.missing_rate_urdb = pickle.load(open('reo/tests/missing_rate.p','rb'))
        self.missing_schedule_urdb = pickle.load(open('reo/tests/missing_schedule.p','rb'))

    @property
    def complete_valid_nestedpost(self):
        return  json.load(open('reo/tests/nestedPOST.json'))

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
            text = "Missing Required for Site in Scenario"
            self.assertTrue(text in str(json.loads(response.content)['Input Errors']['Data Validation Errors']))


        electric_tarrif_cases = [['urdb_response','blended_monthly_rates_us_dollars_per_kwh','monthly_demand_charges_us_dollars_per_kw'],['urdb_response','monthly_demand_charges_us_dollars_per_kw'],['urdb_response','blended_monthly_rates_us_dollars_per_kwh']]
        for c in electric_tarrif_cases:
            test_case = self.complete_valid_nestedpost
            for r in c:
                del test_case['Scenario']['Site']['ElectricTariff'][r]
            response = self.get_response(test_case)
            text = "Missing Required for ElectricTariff in Scenario/Site"
            self.assertTrue(text in str(json.loads(response.content)['Input Errors']['Data Validation Errors']))

        load_profile_cases = [['doe_reference_name','annual_kwh','monthly_totals_kwh','loads_kw'],['loads_kw','monthly_totals_kwh','annual_kwh'],  ['loads_kw','doe_reference_name','annual_kwh']]
        for c in load_profile_cases:
            test_case = self.complete_valid_nestedpost
            for r in c:
                del test_case['Scenario']['Site']['LoadProfile'][r]
            response = self.get_response(test_case)
            text = "Missing Required for LoadProfile in Scenario/Site"
            self.assertTrue(text in str(json.loads(response.content)['Input Errors']['Data Validation Errors']))


    def swap_attr(dictionary, location, attr, value):
        base_dictionary = json.load(open('reo/tests/nested_json.json'))

        i = 0
        for key,num in location:
            if i==0:
                dictionary = base_dictionary[key]
                i+=1
            else:
                dictionary = dictionary[key]

                if num is not None:
                    dictionary = dictionary[num]

            dictionary[attr] = value

        return base_dictionary

    def recursive_attribute_read(self, function, dictionary, location = []):

        for attribute,value in dictionary.items():
            if attribute[0] == attribute[0].lower() and attribute[0] not in ['_']:
                function(attribute, value, location = location)

            if attribute[0] == attribute[0].upper():
                if attribute[-1] == 's':
                    for i, item in enumerate(value):
                        new_loc = copy.copy(location)
                        new_loc.append([attribute, i])
                        self.recursive_attribute_read(function,item, new_loc)
                else:
                    new_loc = copy.copy(location)
                    new_loc.append([attribute, None])
                    self.recursive_attribute_read(function, value, new_loc)

    def test_valid_data_types(self):

        def function(attribute,value,location = []):
            if type(value) in [float, int, list, dict]:
                data = self.swap_attr(location, attribute,"A")

                response = self.get_response(data)
                text = "Could not convert " + attribute
                print attribute
                self.assertTrue(text in str(json.loads(response.content)['Input Errors']['Data Validation Errors']))
                self.assertTrue("(A)" in str(json.loads(response.content)['Input Errors']['Data Validation Errors']))

        self.recursive_attribute_read(function, self.complete_valid_nestedpost)

    def test_valid_data_ranges(self):

        def function(attribute,value,location=[]):

            object_name = location[-1][0]
            if object_name[-1] == 's':
                object_name = object_name[:-1]

            data_defintion = self.data_definitions[object_name][attribute]
            text = ''

            if data_defintion.get('min') is not None:
                value = -1e20
                text = "exceeds allowable min"

            if data_defintion.get('max') is not None:
                value = 1e20
                text = "exceeds allowable max"

            if bool(data_defintion.get('restrict_to')):
                value = "12312321"
                text = "not in allowable inputs"

            if text:
                data = self.swap_attr(location, attribute, value)
                response = self.get_response(data)
                self.assertTrue(text in str(json.loads(response.content)['Input Errors']['Data Validation Errors']))

        self.recursive_attribute_read(function, self.complete_valid_nestedpost)

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


    # def test_valid_test_defaults(self):
    # Can't test until we work through new workflow
    #     swaps = [['urdb_rate'], ['demand_charge', 'blended_utility_rate']]
    #     null = None
    #     data = {"losses":null,"roof_area":5000.0,"owner_tax_rate":null,"pv_itc_federal":null,"batt_can_gridcharge":True,"load_profile_name":"RetailStore","batt_replacement_cost_kwh":null,"pv_rebate_state_max":null,"pv_rebate_utility":null,"pv_ibi_utility":null,"pv_rebate_federal":null,"analysis_period":null,"pv_rebate_state":null,"offtaker_tax_rate":null,"pv_macrs_schedule":5,"pv_kw_max":null,"load_size":10000000.0,"tilt":null,"batt_kwh_max":null,"pv_rebate_federal_max":null,"batt_replacement_cost_kw":null,"batt_rebate_total":null,"longitude":-118.1164613,"pv_ibi_state":null,"batt_kw_max":null,"pv_pbi":null,"batt_inverter_efficiency":null,"offtaker_discount_rate":null,"batt_efficiency":null,"batt_soc_min":null,"batt_macrs_schedule":5,"batt_replacement_year_kwh":null,"latitude":34.5794343,"owner_discount_rate":null,"batt_replacement_year_kw":null,"module_type":1,"batt_kw_min":null,"array_type":1,"rate_escalation":null,"batt_cost_kw":null,"pv_kw_min":null,"pv_pbi_max":null,"pv_pbi_years":null,"land_area":1.0,"dc_ac_ratio":null,"net_metering_limit":null,"batt_itc_total":null,"azimuth":null,"batt_soc_init":null,"pv_rebate_utility_max":null,"pv_ibi_utility_max":null,"pv_itc_federal_max":null,"urdb_rate":{"sector":"Commercial","peakkwcapacitymax":200,"energyweekdayschedule":[[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[2,2,2,2,2,2,2,2,3,3,3,3,4,4,4,4,4,4,3,3,3,3,3,2],[2,2,2,2,2,2,2,2,3,3,3,3,4,4,4,4,4,4,3,3,3,3,3,2],[2,2,2,2,2,2,2,2,3,3,3,3,4,4,4,4,4,4,3,3,3,3,3,2],[2,2,2,2,2,2,2,2,3,3,3,3,4,4,4,4,4,4,3,3,3,3,3,2],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0]],"demandattrs":[{"Facilties Voltage Discount (2KV-<50KV)":"$-0.18/KW"},{"Facilties Voltage Discount >50 kV-<220kV":"$-5.78/KW"},{"Facilties Voltage Discount >220 kV":"$-9.96/KW"},{"Time Voltage Discount (2KV-<50KV)":"$-0.70/KW"},{"Time Voltage Discount >50 kV-<220kV":"$-1.93/KW"},{"Time Voltage Discount >220 kV":"$-1.95/KW"}],"energyratestructure":[[{"rate":0.0712,"unit":"kWh"}],[{"rate":0.09368,"unit":"kWh"}],[{"rate":0.066,"unit":"kWh"}],[{"rate":0.08888,"unit":"kWh"}],[{"rate":0.1355,"unit":"kWh"}]],"energyweekendschedule":[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],"demandweekendschedule":[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],"utility":"Southern California Edison Co","flatdemandstructure":[[{"rate":13.2}]],"startdate":1433116800,"phasewiring":"Single Phase","source":"http://www.sce.com/NR/sc3/tm2/pdf/ce30-12.pdf","label":"55fc81d7682bea28da64f9ae","flatdemandunit":"kW","eiaid":17609,"voltagecategory":"Primary","revisions":[1433408708,1433409358,1433516188,1441198316,1441199318,1441199417,1441199824,1441199996,1454521683],"demandweekdayschedule":[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,0],[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,0],[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,0],[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],"voltageminimum":2000,"description":"- Energy tiered charge = generation charge + delivery charge\r\n\r\n- Time of day demand charges (generation-based) are to be added to the monthly demand charge(Delivery based).","energyattrs":[{"Voltage Discount (2KV-<50KV)":"$-0.00106/Kwh"},{"Voltage Discount (>50 KV<220 KV)":"$-0.00238/Kwh"},{"Voltage Discount at 220 KV":"$-0.0024/Kwh"},{"California Climate credit":"$-0.00669/kwh"}],"demandrateunit":"kW","flatdemandmonths":[0,0,0,0,0,0,0,0,0,0,0,0],"approved":True,"fixedmonthlycharge":259.2,"enddate":1451520000,"name":"Time of Use, General Service, Demand Metered, Option B: GS-2 TOU B, Single Phase","country":"USA","uri":"http://en.openei.org/apps/IURDB/rate/view/55fc81d7682bea28da64f9ae","voltagemaximum":50000,"peakkwcapacitymin":20,"peakkwcapacityhistory":12,"demandratestructure":[[{"rate":0}],[{"rate":5.3}],[{"rate":18.11}]]},"pv_cost":null,"rate_inflation":null,"batt_kwh_min":null,"pv_ibi_state_max":null,"pv_pbi_system_max":null,"batt_rectifier_efficiency":null,"pv_om":null,"batt_cost_kwh":null,"crit_load_factor":1.0}

    #     for add in swaps:
    #        # Test All  Data and  Valid Rate Inputs

    #         if add == swaps[1]:
    #             del data['urdb_rate']
    #             del data['load_size']
    #             data['load_monthly_kwh'] = [100, 200, 250, 300, 350, 350, 400, 400, 350, 250, 250, 200]
    #             data['blended_utility_rate'] = [i*2 for i in [0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066, 0.05066]]
    #             data['demand_charge'] = [10.00, 10.00, 10.00, 10.00, 10.00, 10.00, 10.00, 10.00, 10.00, 10.00, 10.00, 10.00]

    #             data = ValidateNestedInput(data, nested=False).input
    #             resp = self.api_client.post(self.reopt_base, format='json', data=data)
    #             self.assertHttpCreated(resp)
    #             d = json.loads(resp.content)

    #             npv = 855.0
    #             lcc = 2998.0
    #             pv_kw = 1.24622
    #             batt_kw = 0.163791
    #             batt_kwh = 0.52211
    #             yr_one = 1488.5226

    #             self.assertTrue((float(d['lcc']) - lcc) / lcc < self.REopt_tol)
    #             self.assertTrue((float(d['npv']) - npv) / npv < self.REopt_tol * 2)  # *2 b/c npv is difference of two outputs
    #             self.assertTrue((float(d['pv_kw']) - pv_kw) / pv_kw < self.REopt_tol)
    #             self.assertTrue((float(d['batt_kw']) - batt_kw) / batt_kw < self.REopt_tol)
    #             self.assertTrue((float(d['batt_kwh']) - batt_kwh) / batt_kwh < self.REopt_tol)
    #             self.assertTrue((float(d['year_one_utility_kwh']) - yr_one) / yr_one < self.REopt_tol)

    #         else:
    #             data = ValidateNestedInput(data, nested=False).input
    #             resp = self.api_client.post(self.reopt_base, format='json', data=data)
    #             self.assertHttpCreated(resp)
    #             d = json.loads(resp.content)

    #             lcc = 12651213.0
    #             npv = 385668.0
    #             pv_kw = 185.798
    #             batt_kw = 200.866
    #             batt_kwh = 960.659
    #             yr_one_kwh = 9709753.5354

    #             self.assertTrue((float(d['lcc']) -lcc) /lcc  < self.REopt_tol)
    #             self.assertTrue((float(d['npv']) - npv) / npv < self.REopt_tol * 2)  # *2 b/c npv is difference of two outputs
    #             self.assertTrue((float(d['pv_kw']) - pv_kw) / pv_kw < self.REopt_tol)
    #             self.assertTrue((float(d['batt_kw']) - batt_kw) / batt_kw < self.REopt_tol)
    #             self.assertTrue((float(d['batt_kwh']) - batt_kwh) / batt_kwh < self.REopt_tol)
#             self.assertTrue((float(d['year_one_utility_kwh']) - yr_one_kwh) / yr_one_kwh < self.REopt_tol)