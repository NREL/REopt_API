# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0085_auto_20201217_2346'),
    ]

    operations = [
                     migrations.RunSQL(
                         "ALTER TABLE reo_loadprofilemodel RENAME COLUMN annual_kwh to annual_kwh_old;"),
                     migrations.RunSQL("ALTER TABLE reo_loadprofilemodel ADD COLUMN annual_kwh double precision;"),
                     migrations.RunSQL(
                         "UPDATE reo_loadprofilemodel SET annual_kwh=annual_kwh_old[0];"),
                     migrations.RunSQL("ALTER TABLE reo_loadprofilemodel DROP COLUMN annual_kwh_old;"),

                     migrations.RunSQL(
                         "ALTER TABLE reo_loadprofileboilerfuelmodel RENAME COLUMN annual_mmbtu to annual_mmbtu_old;"),
                     migrations.RunSQL("ALTER TABLE reo_loadprofileboilerfuelmodel ADD COLUMN annual_mmbtu double precision;"),
                     migrations.RunSQL(
                         "UPDATE reo_loadprofileboilerfuelmodel SET annual_mmbtu=annual_mmbtu_old[0];"),
                     migrations.RunSQL("ALTER TABLE reo_loadprofileboilerfuelmodel DROP COLUMN annual_mmbtu_old;"),

                     migrations.RunSQL(
                         "ALTER TABLE reo_loadprofilechillerthermalmodel RENAME COLUMN annual_tonhour to annual_tonhour_old;"),
                     migrations.RunSQL("ALTER TABLE reo_loadprofilechillerthermalmodel ADD COLUMN annual_tonhour double precision;"),
                     migrations.RunSQL(
                         "UPDATE reo_loadprofilechillerthermalmodel SET annual_tonhour=annual_tonhour_old[0];"),
                     migrations.RunSQL("ALTER TABLE reo_loadprofilechillerthermalmodel DROP COLUMN annual_tonhour_old;"),
    ]
    
