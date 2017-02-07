# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0008_runoutput_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runinput',
            name='user_id',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='runoutput',
            name='user_id',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
