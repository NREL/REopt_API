# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resilience', '0002_resiliencecase_api_version'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resiliencecase',
            old_name='load_8760_kw',
            new_name='load_8760_kwh',
        ),
        migrations.RenameField(
            model_name='resiliencecase',
            old_name='pv_resource',
            new_name='pv_resource_kwh',
        ),
    ]
