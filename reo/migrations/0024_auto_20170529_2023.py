# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0023_auto_20170517_2221'),
    ]

    operations = [
        migrations.AddField(
            model_name='runinput',
            name='crit_load_factor',
            field=models.FloatField(null=True, blank=True),

        ),
        migrations.AddField(
            model_name='runoutput',
            name='crit_load_factor',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
