# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0016_auto_20170920_2157'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runinput',
            old_name='rate_inflation',
            new_name='om_cost_growth_rate',
        ),
        migrations.RenameField(
            model_name='runoutput',
            old_name='rate_inflation',
            new_name='om_cost_growth_rate',
        ),
    ]
