# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0008_auto_20171222_2234'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneratorModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('run_uuid', models.UUIDField(unique=True)),
                ('size_kw', models.FloatField()),
                ('fuel_slope_gal_per_kwh', models.FloatField()),
                ('fuel_intercept_gal', models.FloatField()),
                ('fuel_avail_gal', models.FloatField()),
                ('min_turn_down_pct', models.FloatField()),
                ('fuel_used_gal', models.FloatField(null=True, blank=True)),
            ],
        ),
    ]
