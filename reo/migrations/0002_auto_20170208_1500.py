# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runoutput',
            old_name='intereconnection_limit',
            new_name='interconnection_limit',
        ),
    ]
