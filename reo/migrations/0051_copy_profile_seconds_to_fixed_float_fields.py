# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0050_auto_20191030_1800'),
    ]

    operations = [

        migrations.RunSQL("UPDATE reo_profilemodel SET parse_run_outputs_seconds2 = cast(parse_run_outputs_seconds as double precision), pre_setup_scenario_seconds2 = cast(pre_setup_scenario_seconds as double precision), reopt_bau_seconds2 = cast(reopt_bau_seconds as double precision), reopt_seconds2 = cast(reopt_seconds as double precision), setup_scenario_seconds2 = cast(setup_scenario_seconds as double precision);"),

    ]