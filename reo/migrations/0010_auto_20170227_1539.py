# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0009_auto_20170223_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='year_one_battery_soc_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_battery_to_grid_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_battery_to_load_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_demand_cost_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_electric_load_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_energy_cost_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_grid_to_battery_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_grid_to_load_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_pv_to_battery_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_pv_to_grid_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_pv_to_load_series',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
    ]
