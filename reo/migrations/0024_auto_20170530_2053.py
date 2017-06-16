# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0023_auto_20170525_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runoutput',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
