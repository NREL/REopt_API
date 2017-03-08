# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0015_auto_20170303_2231'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='time_steps_per_hour',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_datetime_start',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
