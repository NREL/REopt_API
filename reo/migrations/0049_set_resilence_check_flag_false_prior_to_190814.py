# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0048_alter_wholesale_rates_array_real'),
    ]

    operations = [

        migrations.RunSQL("UPDATE reo_loadprofilemodel SET resilience_check_flag = False WHERE reo_loadprofilemodel.run_uuid IN (select run_uuid from reo_scenariomodel WHERE created < '2019-08-14 14:50:00');"),

    ]
