# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0045_generatormodel_fuel_used_gal_bau'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loadprofilemodel',
            name='resilience_check_flag',
            field=models.BooleanField(default=False),
        ),
    ]
