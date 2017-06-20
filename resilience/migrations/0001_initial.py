# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ResilienceCase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('load_8760_kw', django.contrib.postgres.fields.ArrayField(default=[], null=True, base_field=models.TextField(blank=True), size=None, blank=True)),
                ('pv_resource', django.contrib.postgres.fields.ArrayField(default=[], null=True, base_field=models.TextField(blank=True), size=None, blank=True)),
            ],
        ),
    ]
