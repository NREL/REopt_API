# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0005_auto_20170208_1723'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runinput',
            old_name='batt_time_max',
            new_name='batt_kwh_max',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='batt_time_min',
            new_name='batt_kwh_min',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='batt_time_max',
            new_name='batt_kwh_max',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='batt_time_min',
            new_name='batt_kwh_min',
        ),
    ]
