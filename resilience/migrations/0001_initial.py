# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ResilienceCase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pv_kw', models.FloatField(null=True, blank=True)),
                ('batt_kw', models.FloatField(null=True, blank=True)),
                ('batt_kwh', models.FloatField(null=True, blank=True)),
                ('load', django.contrib.postgres.fields.ArrayField(default=[], null=True, base_field=models.FloatField(blank=True), size=None, blank=True)),
                ('prod_factor', django.contrib.postgres.fields.ArrayField(default=[], null=True, base_field=models.FloatField(blank=True), size=None, blank=True)),
                ('init_soc', django.contrib.postgres.fields.ArrayField(default=[], null=True, base_field=models.FloatField(blank=True), size=None, blank=True)),
                ('crit_load_factor', models.FloatField(null=True, blank=True)),
                ('batt_roundtrip_efficiency', models.FloatField(null=True, blank=True)),
                ('api_version', models.TextField(default=b'', blank=True)),
                ('r_list', django.contrib.postgres.fields.ArrayField(default=[], null=True, base_field=models.FloatField(null=True, blank=True), size=None, blank=True)),
                ('r_min', models.FloatField(null=True, blank=True)),
                ('r_max', models.FloatField(null=True, blank=True)),
                ('r_avg', models.FloatField(null=True, blank=True)),
            ],
        ),
    ]
