# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0024_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='electrictariffmodel',
            name='add_blended_rates_to_urdb_rate',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
