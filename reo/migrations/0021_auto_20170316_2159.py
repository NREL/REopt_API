# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0020_auto_20170316_2107'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='total_demand_cost_bau',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='total_energy_cost_bau',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
