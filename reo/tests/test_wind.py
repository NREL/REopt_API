import json
from tastypie.test import ResourceTestCaseMixin
from reo.nested_to_flat_output import nested_to_flat
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from reo.models import ModelManager
from reo.utilities import check_common_outputs


class WindTests(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(WindTests, self).setUp()
        self.reopt_base = '/v1/job/'

    def get_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)

    def test_wind(self):
        """
        Validation run for wind scenario that matches REopt desktop results as of 9/26/17.
        Note no tax, no ITC, no MACRS.
        :return:
        """

        wind_post = {"Scenario": {"Site": {
            "LoadProfile": {
                "annual_kwh": 10000000,
                "doe_reference_name": "MediumOffice"
            },
            "Storage": {
                "max_kwh": 0,
                "max_kw": 0
            },
            "latitude": 39.91065, "longitude": -105.2348,
            "PV": {
                "max_kw": 0
            },
            "Wind": {
                "macrs_bonus_pct": 0.0,
                "max_kw": 10000,
                "federal_itc_pct": 0,
                "macrs_option_years": 0
            },
            "Financial": {
                "om_cost_escalation_pct": 0.001,
                "escalation_pct": 0.006,
                "offtaker_discount_pct": 0.07,
                "analysis_years": 25,
                "offtaker_tax_pct": 0.0
            },
            "ElectricTariff": {
                "blended_monthly_demand_charges_us_dollars_per_kw": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "net_metering_limit_kw": 1e6,
                "blended_monthly_rates_us_dollars_per_kwh": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
            }
        }}}

        d_expected = dict()
        d_expected['lcc'] = 9849424
        d_expected['npv'] = 14861356
        d_expected['wind_kw'] = 4077.9
        d_expected['average_annual_energy_exported_wind'] = 5751360
        d_expected['net_capital_costs_plus_om'] = 9835212

        resp = self.get_response(data=wind_post)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)
        c = nested_to_flat(d['outputs'])

        try:
            check_common_outputs(self, c, d_expected)
        except:
            print("Run {} expected outputs may have changed. Check the Outputs folder.".format(run_uuid))
            print("Error message: {}".format(d['messages']))
            raise
