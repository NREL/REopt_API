# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0002_runoutput_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='user_id',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
