# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0007_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financialmodel',
            name='owner_discount_pct',
        ),
        migrations.RemoveField(
            model_name='financialmodel',
            name='owner_tax_pct',
        ),
    ]
