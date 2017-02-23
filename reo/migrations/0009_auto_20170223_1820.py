# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0008_auto_20170222_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='runinput',
            name='load_year',
            field=models.IntegerField(default=2018, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='load_year',
            field=models.IntegerField(default=2018, null=True, blank=True),
        ),
    ]
