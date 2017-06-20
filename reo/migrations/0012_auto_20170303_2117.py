# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0011_auto_20170303_2107'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runinput',
            old_name='batt_itc_local',
            new_name='batt_itc_utility',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='batt_itc_local_max',
            new_name='batt_itc_utility_max',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_itc_local',
            new_name='pv_itc_utility',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_itc_local_max',
            new_name='pv_itc_utility_max',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_pbi_local',
            new_name='pv_pbi_utility',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_pbi_local_max',
            new_name='pv_pbi_utility_max',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_pbi_local_system_max',
            new_name='pv_pbi_utility_system_max',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_pbi_local_years',
            new_name='pv_pbi_utility_years',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='batt_itc_local',
            new_name='batt_itc_utility',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='batt_itc_local_max',
            new_name='batt_itc_utility_max',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_itc_local',
            new_name='pv_itc_utility',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_itc_local_max',
            new_name='pv_itc_utility_max',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_pbi_local',
            new_name='pv_pbi_utility',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_pbi_local_max',
            new_name='pv_pbi_utility_max',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_pbi_local_system_max',
            new_name='pv_pbi_utility_system_max',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_pbi_local_years',
            new_name='pv_pbi_utility_years',
        ),
    ]
