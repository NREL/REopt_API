# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0020_auto_20180713_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='errormodel',
            name='user_id',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
