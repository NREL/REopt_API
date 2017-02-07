# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0009_auto_20170207_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='runinput',
            name='interconnection_limit',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='net_metering_limit',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wholesale_rate',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
