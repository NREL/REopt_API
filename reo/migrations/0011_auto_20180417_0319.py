# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0010_auto_20180416_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialmodel',
            name='microgrid_upgrade_cost_pct',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='financialmodel',
            name='microgrid_upgrade_cost_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
