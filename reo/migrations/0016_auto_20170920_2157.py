# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0015_auto_20170920_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='total_min_charge_adder',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='total_min_charge_adder_bau',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_min_charge_adder',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_min_charge_adder_bau',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
