# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0030_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadprofilemodel',
            name='annual_calculated_kwh',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
