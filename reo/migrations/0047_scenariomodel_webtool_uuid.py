# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0046_auto_20191016_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenariomodel',
            name='webtool_uuid',
            field=models.TextField(null=True, blank=True),
        ),
    ]
