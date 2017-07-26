# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0007_auto_20170718_2322'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResilienceModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resilience_by_timestep', django.contrib.postgres.fields.ArrayField(null=True, base_field=models.FloatField(null=True), size=None)),
                ('resilience_hours_min', models.FloatField(null=True)),
                ('resilience_hours_max', models.FloatField(null=True)),
                ('resilience_hours_avg', models.FloatField(null=True)),
                ('run_output', models.ForeignKey(to='reo.RunOutput')),
            ],
        ),
    ]
