# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0002_auto_20170626_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runinput',
            name='timeout',
            field=models.IntegerField(default=295, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='runoutput',
            name='timeout',
            field=models.IntegerField(default=295, null=True, blank=True),
        ),
    ]
