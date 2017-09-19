# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('resilience_stats', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resiliencemodel',
            name='outage_durations',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=models.FloatField(null=True), size=None),
        ),
        migrations.AddField(
            model_name='resiliencemodel',
            name='probs_of_surviving',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=models.FloatField(null=True), size=None),
        ),
    ]
