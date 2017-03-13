# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0017_runinput_time_steps_per_hour'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runinput',
            name='pv_pbi_state',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='pv_pbi_state_max',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='pv_pbi_state_system_max',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='pv_pbi_state_years',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='pv_pbi_utility',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='pv_pbi_utility_max',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='pv_pbi_utility_system_max',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='pv_pbi_utility_years',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='pv_pbi_state',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='pv_pbi_state_max',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='pv_pbi_state_system_max',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='pv_pbi_state_years',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='pv_pbi_utility',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='pv_pbi_utility_max',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='pv_pbi_utility_system_max',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='pv_pbi_utility_years',
        ),
    ]
