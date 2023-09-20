# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0028_auto_20180920_2151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='electrictariffmodel',
            name='blended_annual_demand_charges_us_dollars_per_kw',
            field=models.FloatField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='electrictariffmodel',
            name='blended_annual_rates_us_dollars_per_kwh',
            field=models.FloatField(default=0, null=True, blank=True),
        ),
    ]
