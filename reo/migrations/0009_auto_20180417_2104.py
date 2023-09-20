# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0008_auto_20171222_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadprofilemodel',
            name='loads_kw_is_net',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='pvmodel',
            name='existing_kw',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
