# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0020_runoutput_inputs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runoutput',
            name='run_input_id',
        ),
    ]
