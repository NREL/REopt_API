# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0006_auto_20161130_0057'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runinput',
            name='rate_tax',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='rate_tax',
        ),
        migrations.AddField(
            model_name='runinput',
            name='offtaker_tax_rate',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='owner_tax_rate',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='offtaker_tax_rate',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='owner_tax_rate',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
