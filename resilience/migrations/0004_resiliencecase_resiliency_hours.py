# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resilience', '0003_auto_20170520_0135'),
    ]

    operations = [
        migrations.AddField(
            model_name='resiliencecase',
            name='resiliency_hours',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
