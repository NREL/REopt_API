# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
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
