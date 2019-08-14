# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0038_auto_20190711_2019'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadprofilemodel',
            name='gen_energy_at_start_of_outage_kwh',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
