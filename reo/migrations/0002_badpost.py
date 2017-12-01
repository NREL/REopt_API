# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BadPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('run_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('post', picklefield.fields.PickledObjectField(editable=False)),
                ('errors', models.TextField()),
            ],
        ),
    ]
