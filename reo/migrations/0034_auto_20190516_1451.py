# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0033_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='pvmodel',
            name='station_distance_km',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='pvmodel',
            name='station_latitude',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='pvmodel',
            name='station_longitude',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
