# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0021_remove_runoutput_run_input_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='REoptResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inputs', picklefield.fields.PickledObjectField(null=True, editable=False)),
                ('outputs', picklefield.fields.PickledObjectField(null=True, editable=False)),
                ('messages', picklefield.fields.PickledObjectField(null=True, editable=False)),
            ],
        ),
    ]
