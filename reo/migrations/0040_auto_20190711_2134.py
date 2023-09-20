# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0039_loadprofilemodel_gen_energy_at_start_of_outage_kwh'),
    ]

    operations = [
        migrations.RenameField(
            model_name='loadprofilemodel',
            old_name='gen_energy_at_start_of_outage_kwh',
            new_name='fuel_avail_before_outage_pct',
        ),
    ]
