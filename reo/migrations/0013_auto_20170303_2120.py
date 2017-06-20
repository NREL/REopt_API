# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0012_auto_20170303_2117'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runinput',
            name='batt_time_max',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='batt_time_min',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='batt_time_max',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='batt_time_min',
        ),
    ]
