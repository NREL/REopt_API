# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0008_auto_20171222_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadprofilemodel',
            name='critical_loads_kw',
            field=django.contrib.postgres.fields.ArrayField(default=[], base_field=models.FloatField(blank=True), size=None),
        ),
    ]
