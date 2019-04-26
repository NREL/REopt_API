# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0034_ipaddressmodel'),
    ]

    operations = [
        migrations.DeleteModel(
            name='IPAddressModel',
        ),
    ]
