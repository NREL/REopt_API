# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0003_errormodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='errormodel',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2017, 12, 7, 0, 8, 39, 263184, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
