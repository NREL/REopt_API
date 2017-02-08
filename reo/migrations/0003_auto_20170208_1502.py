# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0002_auto_20170208_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='runinput',
            name='tilt',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='tilt',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
