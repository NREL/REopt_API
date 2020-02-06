# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0010_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadprofilemodel',
            name='critical_loads_kw_is_net',
            field=models.BooleanField(default=False),
        ),
    ]
