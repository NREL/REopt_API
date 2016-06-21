# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reoptrun',
            old_name='net_present_value',
            new_name='lcc',
        ),
        migrations.AddField(
            model_name='reoptrun',
            name='npv',
            field=models.FloatField(default=0.0),
        ),
    ]
