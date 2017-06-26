# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='runinput',
            name='timeout',
            field=models.IntegerField(default=295, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='timeout',
            field=models.IntegerField(default=295, blank=True),
        ),
    ]
