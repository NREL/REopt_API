# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0048_alter_wholesale_rates_array_real'),
    ]

    operations = [
        migrations.RenameField(
            model_name='generatormodel',
            old_name='existing_gen_fixed_om_cost_us_dollars_bau',
            new_name='existing_gen_total_fixed_om_cost_us_dollars',
        ),
        migrations.RenameField(
            model_name='generatormodel',
            old_name='existing_gen_variable_om_cost_us_dollars_bau',
            new_name='existing_gen_total_variable_om_cost_us_dollars',
        ),
        migrations.RenameField(
            model_name='generatormodel',
            old_name='gen_variable_om_cost_us_dollars',
            new_name='total_variable_om_cost_us_dollars',
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='existing_gen_total_fuel_cost_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='existing_gen_year_one_fuel_cost_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='existing_gen_year_one_variable_om_cost_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='total_fuel_cost_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='year_one_fuel_cost_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='year_one_variable_om_cost_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='electrictariffmodel',
            name='wholesale_rate_above_site_load_us_dollars_per_kwh',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(default=[0]), size=None),
        ),
        migrations.AlterField(
            model_name='electrictariffmodel',
            name='wholesale_rate_us_dollars_per_kwh',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(default=[0]), size=None),
        ),
    ]
