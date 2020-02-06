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
        ('reo', '0034_auto_20190516_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatormodel',
            name='average_yearly_energy_exported_kwh',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='average_yearly_energy_produced_kwh',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='diesel_fuel_cost_us_dollars_per_gallon',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='existing_gen_om_cost_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='existing_kw',
            field=models.FloatField(default=0, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='generator_only_runs_during_grid_outage',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='generator_sells_energy_back_to_grid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='installed_cost_us_dollars_per_kw',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='max_kw',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='min_kw',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='om_cost_us_dollars_per_kw',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='om_cost_us_dollars_per_kwh',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='year_one_energy_produced_kwh',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='year_one_power_production_series_kw',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='year_one_to_battery_series_kw',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='generatormodel',
            name='year_one_to_grid_series_kw',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.FloatField(null=True, blank=True), blank=True),
        ),
        migrations.AlterField(
            model_name='generatormodel',
            name='fuel_avail_gal',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='generatormodel',
            name='fuel_intercept_gal_per_hr',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='generatormodel',
            name='fuel_slope_gal_per_kwh',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='generatormodel',
            name='min_turn_down_pct',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='generatormodel',
            name='size_kw',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
