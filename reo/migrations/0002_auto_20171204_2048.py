# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badpost',
            name='run_uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='electrictariffmodel',
            name='run_uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='financialmodel',
            name='run_uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='loadprofilemodel',
            name='run_uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='messagemodel',
            name='run_uuid',
            field=models.UUIDField(),
        ),
        migrations.AlterField(
            model_name='pvmodel',
            name='run_uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='scenariomodel',
            name='run_uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='sitemodel',
            name='run_uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='storagemodel',
            name='run_uuid',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='windmodel',
            name='run_uuid',
            field=models.UUIDField(unique=True),
        ),
    ]
