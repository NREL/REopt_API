# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0021_auto_20170316_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='lcc_bau',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
