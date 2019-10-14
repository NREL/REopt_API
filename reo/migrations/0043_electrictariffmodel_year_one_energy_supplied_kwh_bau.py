# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0042_scenariomodel_job_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='electrictariffmodel',
            name='year_one_energy_supplied_kwh_bau',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
