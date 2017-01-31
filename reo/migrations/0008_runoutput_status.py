# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0007_auto_20170120_2128'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='status',
            field=models.TextField(null=True, blank=True),
        ),
    ]
