# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0034_auto_20190516_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='electrictariffmodel',
            name='wholesale_rate_above_site_load_us_dollars_per_kwh',
            field=models.FloatField(default=0),
        ),
    ]
