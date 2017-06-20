# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0007_auto_20170216_1806'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='irr',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_demand_cost',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_energy_cost',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
