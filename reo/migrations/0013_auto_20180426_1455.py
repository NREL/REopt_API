# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0012_loadprofilemodel_outage_is_major_event'),
    ]

    operations = [
        migrations.RenameField(
            model_name='generatormodel',
            old_name='fuel_intercept_gal',
            new_name='fuel_intercept_gal_per_hr',
        ),
    ]
