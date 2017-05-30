# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0022_runoutput_lcc_bau'),
    ]

    operations = [
        #migrations.RemoveField(
        #    model_name='runoutput',
        #    name='id',
        #),
        migrations.AddField(
            model_name='runoutput',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
    ]
