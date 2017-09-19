# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0009_auto_20170821_1639'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_itc_state',
            new_name='pv_ibi_state',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_itc_state_max',
            new_name='pv_ibi_state_max',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_itc_utility',
            new_name='pv_ibi_utility',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_itc_utility_max',
            new_name='pv_ibi_utility_max',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_itc_state',
            new_name='pv_ibi_state',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_itc_state_max',
            new_name='pv_ibi_state_max',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_itc_utility',
            new_name='pv_ibi_utility',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_itc_utility_max',
            new_name='pv_ibi_utility_max',
        ),
    ]
