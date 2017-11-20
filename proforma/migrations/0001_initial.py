# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    operations = [
        migrations.CreateModel(
            name='ProForma',
            fields=[
                ('scenariomodel', models.OneToOneField(primary_key=True, default=0, serialize=False, to='reo.ScenarioModel', blank=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4)),
                ('spreadsheet_created', models.DateTimeField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
