# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0020_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitemodel',
            name='location',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sitemodel',
            name='run_description',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
