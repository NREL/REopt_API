# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resilience_stats', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resiliencemodel',
            name='scenario_model',
        ),
        migrations.AddField(
            model_name='resiliencemodel',
            name='scenariomodel',
            field=models.OneToOneField(null=True, default=None, blank=True, to='reo.ScenarioModel'),
        ),
    ]
