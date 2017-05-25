# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('resilience', '0004_resiliencecase_resiliency_hours'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resiliencecase',
            old_name='resiliency_hours',
            new_name='batt_kw',
        ),
        migrations.RenameField(
            model_name='resiliencecase',
            old_name='load_8760_kwh',
            new_name='crit_load_factor',
        ),
        migrations.RenameField(
            model_name='resiliencecase',
            old_name='pv_resource_kwh',
            new_name='init_soc',
        ),
        migrations.AddField(
            model_name='resiliencecase',
            name='batt_kwh',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='resiliencecase',
            name='batt_roundtrip_efficiency',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='resiliencecase',
            name='load',
            field=django.contrib.postgres.fields.ArrayField(default=[], null=True, base_field=models.TextField(blank=True), size=None, blank=True),
        ),
        migrations.AddField(
            model_name='resiliencecase',
            name='prod_factor',
            field=django.contrib.postgres.fields.ArrayField(default=[], null=True, base_field=models.TextField(blank=True), size=None, blank=True),
        ),
        migrations.AddField(
            model_name='resiliencecase',
            name='pv_kw',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='resiliencecase',
            name='r_avg',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='resiliencecase',
            name='r_list',
            field=django.contrib.postgres.fields.ArrayField(default=[], null=True, base_field=models.FloatField(null=True, blank=True), size=None, blank=True),
        ),
        migrations.AddField(
            model_name='resiliencecase',
            name='r_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='resiliencecase',
            name='r_min',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
