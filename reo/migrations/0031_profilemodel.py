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
                ('pre_setup_scenario', models.FloatField(default=b'', null=True)),
                ('setup_scenario', models.FloatField(default=b'', null=True)),
                ('reopt', models.FloatField(default=b'', null=True)),
                ('reopt_bau', models.FloatField(default=b'', null=True)),
                ('parse_run_outputs', models.FloatField(default=b'', null=True)),
            ],
        ),
    ]
