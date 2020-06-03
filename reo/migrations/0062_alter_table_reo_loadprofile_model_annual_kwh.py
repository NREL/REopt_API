# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0061_merge_20200520_2158'),
    ]

    operations = [

                     migrations.RunSQL(
                         "ALTER TABLE reo_loadprofilemodel ALTER COLUMN annual_kwh TYPE real USING annual_kwh::real;"),
                     migrations.RunSQL(
                         "ALTER TABLE reo_loadprofilemodel ALTER COLUMN annual_kwh DROP DEFAULT, ALTER COLUMN annual_kwh TYPE real[] USING array[annual_kwh], ALTER COLUMN annual_kwh SET DEFAULT '{}'"),
                     migrations.RunSQL(
                         "ALTER TABLE reo_loadprofilemodel RENAME COLUMN doe_reference_name to doe_reference_name_old;"),
                     migrations.RunSQL("ALTER TABLE reo_loadprofilemodel ADD COLUMN doe_reference_name text[];"),
                     migrations.RunSQL(
                         "UPDATE reo_loadprofilemodel SET doe_reference_name=ARRAY[doe_reference_name_old];"),
                     migrations.RunSQL("ALTER TABLE reo_loadprofilemodel DROP COLUMN doe_reference_name_old;"),

    ]