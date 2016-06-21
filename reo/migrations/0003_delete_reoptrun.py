# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0002_auto_20160419_1046'),
    ]

    operations = [
        migrations.DeleteModel(
            name='REoptRun',
        ),
    ]
