# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0014_auto_20170913_2333'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='total_fixed_cost',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='total_fixed_cost_bau',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_fixed_cost',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_fixed_cost_bau',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
