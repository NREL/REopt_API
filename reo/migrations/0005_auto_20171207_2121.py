# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0004_errormodel_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badpost',
            name='post',
            field=models.TextField(),
        ),
    ]
