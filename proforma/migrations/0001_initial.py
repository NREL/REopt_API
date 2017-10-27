# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProForma',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4)),
                ('spreadsheet_created', models.DateTimeField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('run_output', models.ForeignKey(to='reo.REoptResponse')),
            ],
        ),
    ]
