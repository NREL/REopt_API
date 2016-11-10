# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0004_auto_20161110_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runinput',
            name='load_profile',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
