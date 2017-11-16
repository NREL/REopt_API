# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0002_scenariomodel_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenariomodel',
            name='user_id',
            field=models.TextField(null=True, blank=True),
        ),
    ]
