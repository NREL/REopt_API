# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0019_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='windmodel',
            name='resource_meters_per_sec',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='windmodel',
            name='size_class',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
