# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0017_auto_20170926_1951'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runinput',
            name='wind_degradation_rate',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='wind_degradation_rate',
        ),
    ]
