# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0008_runoutput_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='interconnection_limit',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='net_metering_limit',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='wholesale_rate',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
