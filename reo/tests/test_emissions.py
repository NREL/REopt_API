import json
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin


class ClassAttributes:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)


class TestEmissions(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(TestEmissions, self).setUp()

        self.emissions_url = '/v1/emissions_profile'
        self.submit_url = '/v1/job/'
        self.results_url = '/v1/job/<run_uuid>/results/'
        self.post = json.loads(open('reo/tests/posts/generatorPOST.json','r').read())

    def get_response(self, data):
        initial_post = self.api_client.post(self.submit_url, format='json', data=data)
        uuid = json.loads(initial_post.content)['run_uuid']
        response = json.loads(self.api_client.get(self.results_url.replace('<run_uuid>', str(uuid))).content)
        return response

    def test_emissions_profile_url(self):
        test = self.api_client.get('/v1/emissions_profile/',data={"latitude":60.27641,"longitude":-144.81502})
        self.assertTrue(json.loads(test.content)['region_abbr'] == 'AK')

        test = self.api_client.get('/v1/emissions_profile/',data={"latitude":21.55329,"longitude":-158.014155})
        self.assertTrue(json.loads(test.content)['region_abbr'] == 'HI-Oahu')

        test = self.api_client.get('/v1/emissions_profile/',data={"latitude":21.97966,"longitude":-159.553226})
        self.assertTrue(json.loads(test.content)['region_abbr'] == 'HI')

        test = self.api_client.get('/v1/emissions_profile/',data={"latitude":45,"longitude":-110})
        self.assertTrue(json.loads(test.content)['region_abbr'] == 'NW')
        
        test = self.api_client.get('/v1/emissions_profile/',data={"latitude":1,"longitude":1})
        self.assertTrue("Your site location (1.0,1.0) is more than 5 miles from the nearest emission region." in str(test.content))

    def test_easiur_and_fuel_urls(self):
        test = self.api_client.get('/v1/easiur_costs/',data={"latitude":30.2672,"longitude":-97.7431,"inflation":0.025})
        self.assertEqual(round(json.loads(test.content)['nox_cost_us_dollars_per_tonne_grid'],3), round(4534.03247048984,3))

        test = self.api_client.get('/v1/fuel_emissions_rates/',data={})

    def test_bad_grid_emissions_profile(self):
        """
        Tests that a poorly formatted utility emissions factor profile does not validate 
        and the optimization does not start
        """
        data = self.post
        data['Scenario']['Site']['ElectricTariff']['emissions_factor_series_lb_CO2_per_kwh'] = [1,2]

        response = json.loads(self.api_client.post(self.submit_url, format='json', data=data).content)

        self.assertTrue('emissions_factor_series_lb_CO2_per_kwh' in response['messages']['input_errors'][0])

    def test_bad_grid_emissions_profile_location_with_health_in_obj(self):
        """
        Tests that a location 5 miles outside the AVERT boundaries does not return an emission
        factor profile - optimization is not stopped and emissions are not calculated
        """
        data = self.post
        data['Scenario']['Site']['latitude'] = 1
        data['Scenario']['Site']['longitude'] = 2
        data['Scenario']['timeout_seconds'] = 1
        data['Scenario']['include_health_in_objective'] = True

        response = json.loads(self.api_client.post(self.submit_url, format='json', data=data).content)

        input_error_to_check = 'To include health emissions in the optimization model, you must either: enter a custom emissions_factor_series for health emissions or a site location within the continental U.S.'
        self.assertTrue(input_error_to_check in response['messages']['input_errors'][1])

    def test_bad_grid_emissions_profile_location(self):
        """
        Tests that a location 5 miles outside the AVERT boundaries and outside of the CAMx grid does not return an emission
        factor profile - optimization is not stopped and grid emissions are set to zero
        """
        data = self.post
        data['Scenario']['Site']['latitude'] = 1
        data['Scenario']['Site']['longitude'] = 1

        response = self.get_response(data)

        text_to_check = "'Emissions Warning': {'error': 'Your site location (1.0,1.0) is more than 5 miles from the nearest emission region. Cannot calculate emissions.'"
        self.assertTrue(text_to_check in response['messages']['warnings'])
        self.assertEqual(response['outputs']['Scenario']['Site']['ElectricTariff']['lifecycle_emissions_tCO2'], 0.0)

