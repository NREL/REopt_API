# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0061_merge_20200520_2158'),
    ]

    operations = [
                     migrations.RunSQL(
                         "ALTER TABLE reo_loadprofilemodel RENAME COLUMN annual_kwh to annual_kwh_old;"),
                     migrations.RunSQL("ALTER TABLE reo_loadprofilemodel ADD COLUMN annual_kwh double precision;"),
                     migrations.RunSQL(
                         "UPDATE reo_loadprofilemodel SET doe_reference_name=ARRAY[doe_reference_name_old];"),
                     migrations.RunSQL("ALTER TABLE reo_loadprofilemodel DROP COLUMN doe_reference_name_old;"),

    ]