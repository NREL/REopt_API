# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0007_auto_20170718_2322'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runoutput',
            name='resilience_by_timestep',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='resilience_hours_avg',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='resilience_hours_max',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='resilience_hours_min',
        ),
    ]
