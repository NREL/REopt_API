# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0002_auto_20171204_2048'),
    ]

    operations = [
        migrations.CreateModel(
            name='ErrorModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task', models.TextField(default=b'', blank=True)),
                ('name', models.TextField(default=b'', blank=True)),
                ('run_uuid', models.TextField(default=b'', blank=True)),
                ('message', models.TextField(default=b'', blank=True)),
                ('traceback', models.TextField(default=b'', blank=True)),
            ],
        ),
    ]
