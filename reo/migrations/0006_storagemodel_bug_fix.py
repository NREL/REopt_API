# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storagemodel',
            name='total_itc_pct',
            field=models.FloatField(),
        ),
    ]