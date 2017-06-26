# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resilience', '0002_auto_20170623_2158'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resiliencecase',
            old_name='prod_factor',
            new_name='pv_kw_ac_hourly',
        ),
    ]
