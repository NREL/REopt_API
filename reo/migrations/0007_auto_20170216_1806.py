# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0006_auto_20170213_2326'),
    ]

    operations = [
        migrations.AddField(
            model_name='runinput',
            name='batt_time_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_time_min',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_time_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_time_min',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
