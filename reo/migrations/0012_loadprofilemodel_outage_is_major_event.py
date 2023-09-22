# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0011_auto_20180417_0319'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadprofilemodel',
            name='outage_is_major_event',
            field=models.BooleanField(default=True),
        ),
    ]
