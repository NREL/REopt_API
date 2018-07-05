# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0017_merge'),
    ]

    operations = [

		migrations.RunSQL("ALTER TABLE reo_pvmodel ALTER COLUMN year_one_power_production_series_kw TYPE real[];"),
		migrations.RunSQL("ALTER TABLE reo_pvmodel ALTER COLUMN year_one_to_battery_series_kw TYPE real[];"),
		migrations.RunSQL("ALTER TABLE reo_pvmodel ALTER COLUMN year_one_to_load_series_kw TYPE real[];"),
		migrations.RunSQL("ALTER TABLE reo_pvmodel ALTER COLUMN year_one_to_grid_series_kw TYPE real[];"),

		migrations.RunSQL("ALTER TABLE reo_electrictariffmodel ALTER COLUMN blended_monthly_rates_us_dollars_per_kwh TYPE real[];"),
		migrations.RunSQL("ALTER TABLE reo_electrictariffmodel ALTER COLUMN blended_monthly_demand_charges_us_dollars_per_kw TYPE real[];"),
		migrations.RunSQL("ALTER TABLE reo_electrictariffmodel ALTER COLUMN year_one_energy_cost_series_us_dollars_per_kwh TYPE real[];"),
		migrations.RunSQL("ALTER TABLE reo_electrictariffmodel ALTER COLUMN year_one_demand_cost_series_us_dollars_per_kw TYPE real[];"),
		migrations.RunSQL("ALTER TABLE reo_electrictariffmodel ALTER COLUMN year_one_to_load_series_kw TYPE real[];"),
		migrations.RunSQL("ALTER TABLE reo_electrictariffmodel ALTER COLUMN year_one_to_battery_series_kw TYPE real[];"),

		migrations.RunSQL("ALTER TABLE reo_loadprofilemodel ALTER COLUMN monthly_totals_kwh TYPE real[];"),
		migrations.RunSQL("ALTER TABLE reo_loadprofilemodel ALTER COLUMN loads_kw TYPE real[];"),
		migrations.RunSQL("ALTER TABLE reo_loadprofilemodel ALTER COLUMN year_one_electric_load_series_kw TYPE real[];"),
		migrations.RunSQL("ALTER TABLE reo_loadprofilemodel ALTER COLUMN critical_loads_kw TYPE real[];"),
		migrations.RunSQL("ALTER TABLE reo_loadprofilemodel ALTER COLUMN critical_load_series_kw TYPE real[];")

    ]		