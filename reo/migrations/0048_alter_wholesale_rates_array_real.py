# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0047_scenariomodel_webtool_uuid'),
    ]

    operations = [

        migrations.RunSQL("ALTER TABLE reo_electrictariffmodel ALTER COLUMN wholesale_rate_us_dollars_per_kwh TYPE real[] USING array[wholesale_rate_us_dollars_per_kwh]::real[], ALTER COLUMN wholesale_rate_above_site_load_us_dollars_per_kwh TYPE real[] USING array[wholesale_rate_above_site_load_us_dollars_per_kwh]::real[];"),

    ]