# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resilience_stats', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resiliencemodel',
            name='avg_critical_load',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='resiliencemodel',
            name='present_worth_factor',
            field=models.FloatField(null=True),
        ),
    ]
