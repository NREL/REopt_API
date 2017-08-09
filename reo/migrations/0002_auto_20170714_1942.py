# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='year_one_energy_produced',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_export_benefit',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
