# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0044_auto_20190930_0134'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatormodel',
            name='fuel_used_gal_bau',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
