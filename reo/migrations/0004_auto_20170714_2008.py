# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0003_runoutput_pv_macrs_bonus_reduction'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_macrs_bonus_reduction',
            new_name='pv_macrs_itc_reduction',
        ),
    ]
