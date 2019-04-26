# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0033_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='IPAddressModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('run_uuid', models.UUIDField(unique=True)),
                ('ip_address', models.TextField(default=b'', null=True, blank=True)),
            ],
        ),
    ]
