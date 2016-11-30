# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0005_auto_20161130_0026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runinput',
            name='urdb_rate',
            field=picklefield.fields.PickledObjectField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='runoutput',
            name='urdb_rate',
            field=picklefield.fields.PickledObjectField(null=True, editable=False),
        ),
    ]
