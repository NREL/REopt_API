# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0023_auto_20170517_2221'),
    ]

    operations = [
        migrations.AddField(
            model_name='runinput',
            name='crit_load_factor',
            field=django.contrib.postgres.fields.ArrayField(default=[], null=True, base_field=models.TextField(blank=True), size=None, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='crit_load_factor',
            field=django.contrib.postgres.fields.ArrayField(default=[], null=True, base_field=models.TextField(blank=True), size=None, blank=True),
        ),
    ]
