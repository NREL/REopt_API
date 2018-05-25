# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0014_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadprofilemodel',
            name='critical_load_series_kw',
            field=django.contrib.postgres.fields.ArrayField(default=[], base_field=models.FloatField(null=True, blank=True), size=None),
        ),
    ]
