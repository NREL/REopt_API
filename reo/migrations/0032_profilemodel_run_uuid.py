# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0031_profilemodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilemodel',
            name='run_uuid',
            field=models.UUIDField(default='12345678-1234-5678-1234-567812345678', unique=True),
            preserve_default=False,
        ),
    ]
