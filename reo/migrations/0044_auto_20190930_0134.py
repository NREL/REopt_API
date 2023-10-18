# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0043_electrictariffmodel_year_one_energy_supplied_kwh_bau'),
    ]

    operations = [
        migrations.RenameField(
            model_name='generatormodel',
            old_name='existing_gen_om_cost_us_dollars',
            new_name='existing_gen_fixed_om_cost_us_dollars_bau',
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='existing_gen_variable_om_cost_us_dollars_bau',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='gen_variable_om_cost_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
