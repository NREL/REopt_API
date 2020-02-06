# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0025_auto_20180730_1718'),
    ]

    operations = [

        migrations.RunSQL("ALTER TABLE reo_windmodel ALTER COLUMN wind_meters_per_sec TYPE real[], ALTER COLUMN wind_direction_degrees TYPE real[], ALTER COLUMN temperature_celsius TYPE real[], ALTER COLUMN pressure_atmospheres TYPE real[];"),

    ]