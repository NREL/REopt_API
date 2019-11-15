# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0050_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='pvmodel',
            name='average_yearly_energy_produced_bau_kwh',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
