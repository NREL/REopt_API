# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resilience', '0005_auto_20170525_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resiliencecase',
            name='crit_load_factor',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
