# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0013_auto_20170303_2120'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runinput',
            old_name='batt_replacement_year',
            new_name='batt_replacement_year_kw',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='rate_degradation',
            new_name='pv_degradation_rate',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='bonus_fraction',
            new_name='pv_macrs_bonus_fraction',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='macrs_itc_reduction',
            new_name='pv_macrs_itc_reduction',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='macrs_years',
            new_name='pv_macrs_schedule',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='batt_replacement_year',
            new_name='batt_replacement_year_kw',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='rate_degradation',
            new_name='pv_degradation_rate',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='bonus_fraction',
            new_name='pv_macrs_bonus_fraction',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='macrs_itc_reduction',
            new_name='pv_macrs_itc_reduction',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='macrs_years',
            new_name='pv_macrs_schedule',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='flag_bonus',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='flag_itc',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='flag_macrs',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='flag_replace_batt',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='flag_bonus',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='flag_itc',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='flag_macrs',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='flag_replace_batt',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='run_input_id',
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_can_gridcharge',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_efficiency',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_inverter_efficiency',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_macrs_bonus_fraction',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_macrs_itc_reduction',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_macrs_schedule',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_rectifier_efficiency',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_replacement_year_kwh',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_soc_init',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_soc_min',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_can_gridcharge',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_efficiency',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_inverter_efficiency',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_macrs_bonus_fraction',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_macrs_itc_reduction',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_macrs_schedule',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_rectifier_efficiency',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_replacement_year_kwh',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_soc_init',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_soc_min',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='runoutput',
            name='user_id',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
