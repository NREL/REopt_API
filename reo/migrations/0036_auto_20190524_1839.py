# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0035_auto_20190522_1453'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatormodel',
            name='federal_itc_pct',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='federal_rebate_us_dollars_per_kw',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='macrs_bonus_pct',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='macrs_itc_reduction',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='macrs_option_years',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='pbi_max_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='pbi_system_max_kw',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='pbi_us_dollars_per_kwh',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='pbi_years',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='state_ibi_max_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='state_ibi_pct',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='state_rebate_max_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='state_rebate_us_dollars_per_kw',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='utility_ibi_max_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='utility_ibi_pct',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='utility_rebate_max_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='utility_rebate_us_dollars_per_kw',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
