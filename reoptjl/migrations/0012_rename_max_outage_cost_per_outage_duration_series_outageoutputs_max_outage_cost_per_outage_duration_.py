# Generated by Django 4.0.4 on 2022-11-04 19:08

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reoptjl', '0011_outageoutputs_electricutilityinputs_outage_durations_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='outageoutputs',
            old_name='max_outage_cost_per_outage_duration_series',
            new_name='max_outage_cost_per_outage_duration',
        ),
        migrations.RenameField(
            model_name='outageoutputs',
            old_name='unserved_load_per_outage_series',
            new_name='unserved_load_per_outage',
        ),
        migrations.AddField(
            model_name='outageoutputs',
            name='generator_fuel_used_per_outage',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='Generator fuel used in each outage modeled.', size=None),
        ),
    ]