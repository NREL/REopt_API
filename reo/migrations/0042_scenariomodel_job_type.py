# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0041_auto_20190722_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenariomodel',
            name='job_type',
            field=models.TextField(null=True, blank=True),
        ),
    ]
