# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0015_loadprofilemodel_critical_load_series_kw'),
    ]

    operations = [
        migrations.AddField(
            model_name='pvmodel',
            name='existing_pv_om_cost_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
