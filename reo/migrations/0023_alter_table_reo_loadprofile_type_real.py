# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0017_merge'),
    ]

    operations = [

        migrations.RunSQL("ALTER TABLE reo_loadprofilemodel ALTER COLUMN monthly_totals_kwh TYPE real[], ALTER COLUMN loads_kw TYPE real[], ALTER COLUMN year_one_electric_load_series_kw TYPE real[], ALTER COLUMN critical_loads_kw TYPE real[], ALTER COLUMN critical_load_series_kw TYPE real[];"),

    ]