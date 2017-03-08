# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0016_auto_20170308_1713'),
    ]

    operations = [
        migrations.AddField(
            model_name='runinput',
            name='time_steps_per_hour',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
