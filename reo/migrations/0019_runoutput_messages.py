# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0018_auto_20170927_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='messages',
            field=picklefield.fields.PickledObjectField(null=True, editable=False),
        ),
    ]
