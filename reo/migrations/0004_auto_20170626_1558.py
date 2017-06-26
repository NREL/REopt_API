# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0003_merge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runoutput',
            old_name='prod_factor',
            new_name='pv_kw_ac_hourly',
        ),
    ]
