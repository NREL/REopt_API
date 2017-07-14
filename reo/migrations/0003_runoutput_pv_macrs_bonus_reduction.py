# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0002_auto_20170714_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='pv_macrs_bonus_reduction',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
