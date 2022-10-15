# Generated by Django 4.0.4 on 2022-09-30 00:10

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resilience_stats', '0012_alter_erpoutputs_cumulative_outage_survival_final_time_step_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='erpinputs',
            name='battery_starting_soc_kwh',
        ),
        migrations.AddField(
            model_name='erpinputs',
            name='battery_starting_soc_series_fraction',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(validators=[django.core.validators.MinValueValidator(0)]), blank=True, default=list, help_text='Battery state of charge fraction when an outage begins, at each timestep. Must be hourly (8,760 samples).', size=None),
        ),
    ]