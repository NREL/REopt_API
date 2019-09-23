# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0043_scenariomodel_flexible_time_steps'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scenariomodel',
            name='flexible_time_steps',
        ),
    ]
