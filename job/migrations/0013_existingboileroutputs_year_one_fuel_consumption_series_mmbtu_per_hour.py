# Generated by Django 4.0.6 on 2022-10-11 18:26

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0012_existingboileroutputs_year_one_thermal_to_tes_series_mmbtu_per_hour'),
    ]

    operations = [
        migrations.AddField(
            model_name='existingboileroutputs',
            name='year_one_fuel_consumption_series_mmbtu_per_hour',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, null=True), default=list, size=None),
        ),
    ]