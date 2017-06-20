# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resilience', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resiliencecase',
            name='api_version',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
