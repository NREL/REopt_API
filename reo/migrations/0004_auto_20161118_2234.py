# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0003_auto_20161111_1133'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runinput',
            old_name='load_profile',
            new_name='load_profile_name',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='load_profile',
            new_name='load_profile_name',
        ),
    ]
