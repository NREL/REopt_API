# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0019_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenariomodel',
            name='description',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sitemodel',
            name='address',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
