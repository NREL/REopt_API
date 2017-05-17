# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0022_runoutput_lcc_bau'),
    ]

    operations = [
        migrations.AddField(
            model_name='runinput',
            name='outage_end',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='outage_start',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='outage_end',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='outage_start',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
