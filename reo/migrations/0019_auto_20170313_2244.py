# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0018_auto_20170313_2241'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_pbi_federal',
            new_name='pv_pbi',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_pbi_federal_max',
            new_name='pv_pbi_max',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_pbi_federal_system_max',
            new_name='pv_pbi_system_max',
        ),
        migrations.RenameField(
            model_name='runinput',
            old_name='pv_pbi_federal_years',
            new_name='pv_pbi_years',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_pbi_federal',
            new_name='pv_pbi',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_pbi_federal_max',
            new_name='pv_pbi_max',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_pbi_federal_system_max',
            new_name='pv_pbi_system_max',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='pv_pbi_federal_years',
            new_name='pv_pbi_years',
        ),
    ]
