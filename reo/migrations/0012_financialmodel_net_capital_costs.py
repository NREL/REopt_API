# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0011_loadprofilemodel_critical_loads_kw_is_net'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialmodel',
            name='net_capital_costs',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
