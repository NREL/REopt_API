# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0003_auto_20170208_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='runinput',
            name='gcr',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='gcr',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
