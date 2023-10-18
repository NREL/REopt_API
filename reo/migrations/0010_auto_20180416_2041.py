# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0009_generatormodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialmodel',
            name='avoided_outage_costs_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='financialmodel',
            name='value_of_lost_load_us_dollars_per_kwh',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
