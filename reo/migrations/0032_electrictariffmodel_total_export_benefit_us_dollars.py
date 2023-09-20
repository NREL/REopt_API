# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0031_loadprofilemodel_annual_calculated_kwh'),
    ]

    operations = [
        migrations.AddField(
            model_name='electrictariffmodel',
            name='total_export_benefit_us_dollars',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
