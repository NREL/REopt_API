# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0051_pvmodel_average_yearly_energy_produced_bau_kwh'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialmodel',
            name='net_om_us_dollars_bau',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
