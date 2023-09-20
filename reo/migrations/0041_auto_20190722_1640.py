# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0040_auto_20190711_2134'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loadprofilemodel',
            name='fuel_avail_before_outage_pct',
        ),
        migrations.RemoveField(
            model_name='loadprofilemodel',
            name='unmet_critical_load_from_generator_kwh',
        ),
        migrations.AddField(
            model_name='loadprofilemodel',
            name='sustain_hours',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
