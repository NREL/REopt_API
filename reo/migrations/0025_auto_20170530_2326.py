# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0024_auto_20170529_2023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runinput',
            name='crit_load_factor',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='runoutput',
            name='crit_load_factor',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
