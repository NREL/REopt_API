# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0030_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('run_uuid', models.UUIDField(unique=True)),
                ('pre_setup_scenario_seconds', models.FloatField(default=b'', null=True)),
                ('setup_scenario_seconds', models.FloatField(default=b'', null=True)),
                ('reopt_seconds', models.FloatField(default=b'', null=True)),
                ('reopt_bau_seconds', models.FloatField(default=b'', null=True)),
                ('parse_run_outputs_seconds', models.FloatField(default=b'', null=True)),
            ],
        ),
    ]
