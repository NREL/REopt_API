# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0017_merge'),
    ]

    operations = [

        migrations.RunSQL("ALTER TABLE reo_pvmodel ALTER COLUMN year_one_power_production_series_kw TYPE real[], ALTER COLUMN year_one_to_battery_series_kw TYPE real[],  ALTER COLUMN year_one_to_load_series_kw TYPE real[], ALTER COLUMN year_one_to_grid_series_kw TYPE real[];"),

    ]		