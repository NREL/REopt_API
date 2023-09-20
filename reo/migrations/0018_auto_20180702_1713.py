# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0017_merge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='urdb_utilty_name',
            new_name='urdb_utility_name',
        ),
    ]
