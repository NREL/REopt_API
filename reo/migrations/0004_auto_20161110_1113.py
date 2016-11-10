# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0003_runoutput_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runoutput',
            name='load_profile',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
