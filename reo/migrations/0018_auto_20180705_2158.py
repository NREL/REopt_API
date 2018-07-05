# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0017_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitemodel',
            name='location',
            field=models.TextField(default=b'', blank=True),
        ),
        migrations.AddField(
            model_name='sitemodel',
            name='run_description',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
