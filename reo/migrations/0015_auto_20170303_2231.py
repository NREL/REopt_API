# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0014_auto_20170303_2159'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runinput',
            name='pv_macrs_itc_reduction',
        ),
        migrations.RemoveField(
            model_name='runoutput',
            name='pv_macrs_itc_reduction',
        ),
        migrations.AddField(
            model_name='runoutput',
            name='run_input_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='runoutput',
            name='user_id',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
