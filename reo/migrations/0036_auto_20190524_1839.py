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
