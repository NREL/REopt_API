# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0026_alter_table_reo_wind_type_real'),
    ]

    operations = [
        migrations.RenameField(
            model_name='errormodel',
            old_name='user_id',
            new_name='user_uuid',
        ),
        migrations.RenameField(
            model_name='scenariomodel',
            old_name='user_id',
            new_name='user_uuid',
        ),
    ]
