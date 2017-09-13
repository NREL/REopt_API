# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0013_auto_20170912_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='average_annual_energy_exported_wind',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='average_wind_energy_produced',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_wind_to_battery_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_wind_to_grid_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_wind_to_load_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
    ]
