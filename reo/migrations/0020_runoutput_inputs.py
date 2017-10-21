# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0019_runoutput_messages'),
    ]

    operations = [
        migrations.AddField(
            model_name='runoutput',
            name='inputs',
            field=picklefield.fields.PickledObjectField(null=True, editable=False),
        ),
    ]
