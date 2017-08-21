# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0008_auto_20170809_2316'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runinput',
            old_name='batt_itc_federal',
            new_name='batt_itc_total',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='batt_rebate_federal',
            new_name='batt_rebate_total',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='batt_itc_federal',
            new_name='batt_itc_total',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='batt_rebate_federal',
            new_name='batt_rebate_total',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='batt_itc_federal_max',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='batt_itc_state',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='batt_itc_state_max',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='batt_itc_utility',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='batt_itc_utility_max',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='batt_rebate_federal_max',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='batt_rebate_state',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='batt_rebate_state_max',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='batt_rebate_utility',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='batt_rebate_utility_max',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='batt_itc_federal_max',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='batt_itc_state',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='batt_itc_state_max',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='batt_itc_utility',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='batt_itc_utility_max',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='batt_rebate_federal_max',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='batt_rebate_state',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='batt_rebate_state_max',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='batt_rebate_utility',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='batt_rebate_utility_max',
        ),
    ]
