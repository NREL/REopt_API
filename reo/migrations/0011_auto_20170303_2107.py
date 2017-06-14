# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0010_auto_20170227_1539'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runinput',
            old_name='rate_itc',
            new_name='pv_itc_federal',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='rate_itc',
            new_name='pv_itc_federal',
        ),
        migrations.RemoveField(
            model_name='runinput',
            name='batt_replacement_cost_escalation',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='batt_replacement_cost_escalation',
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_itc_federal',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_itc_federal_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_itc_local',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_itc_local_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_itc_state',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_itc_state_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_rebate_federal',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_rebate_federal_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_rebate_state',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_rebate_state_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_rebate_utility',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='batt_rebate_utility_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_itc_federal_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_itc_local',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_itc_local_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_itc_state',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_itc_state_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_pbi_federal',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_pbi_federal_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_pbi_federal_system_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_pbi_federal_years',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_pbi_local',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_pbi_local_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_pbi_local_system_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_pbi_local_years',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_pbi_state',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_pbi_state_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_pbi_state_system_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_pbi_state_years',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_rebate_federal',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_rebate_federal_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_rebate_state',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_rebate_state_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_rebate_utility',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='pv_rebate_utility_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_itc_federal',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_itc_federal_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_itc_local',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_itc_local_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_itc_state',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_itc_state_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_rebate_federal',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_rebate_federal_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_rebate_state',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_rebate_state_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_rebate_utility',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='batt_rebate_utility_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_itc_federal_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_itc_local',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_itc_local_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_itc_state',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_itc_state_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_pbi_federal',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_pbi_federal_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_pbi_federal_system_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_pbi_federal_years',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_pbi_local',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_pbi_local_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_pbi_local_system_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_pbi_local_years',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_pbi_state',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_pbi_state_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_pbi_state_system_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_pbi_state_years',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_rebate_federal',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_rebate_federal_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_rebate_state',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_rebate_state_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_rebate_utility',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='pv_rebate_utility_max',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
