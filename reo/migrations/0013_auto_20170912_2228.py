# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0012_auto_20170912_2218'),
    ]

    operations = [
        migrations.AddField(
            model_name='runinput',
            name='wind_cost',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_degradation_rate',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_ibi_state',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_ibi_state_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_ibi_utility',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_ibi_utility_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_itc_federal',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_itc_federal_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_kw_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_kw_min',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_macrs_bonus_fraction',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_macrs_itc_reduction',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_macrs_schedule',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_om',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_pbi',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_pbi_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_pbi_system_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_pbi_years',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_rebate_federal',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_rebate_federal_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_rebate_state',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_rebate_state_max',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_rebate_utility',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runinput',
            name='wind_rebate_utility_max',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
