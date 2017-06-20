# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0004_auto_20170208_1503'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runinput',
            old_name='intereconnection_limit',
            new_name='interconnection_limit',
        ),
    ]
