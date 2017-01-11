# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runinput',
            name='building_type',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='building_type',
        ),
    ]
