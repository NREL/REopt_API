# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0004_auto_20161118_2234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runoutput',
            name='urdb_rate',
            field=picklefield.fields.PickledObjectField(editable=False),
        ),
    ]
