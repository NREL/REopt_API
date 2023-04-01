# Generated by Django 4.0.4 on 2023-03-31 22:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0033_generatorinputs_fuel_higher_heating_value_kwh_per_gal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialinputs',
            name='value_of_lost_load_per_kwh',
            field=models.FloatField(blank=True, default=0, help_text='Value placed on unmet site load during grid outages. Units are US dollars per unmet kilowatt-hour. The value of lost load (VoLL) is used to determine outage costs by multiplying VoLL by unserved load for each outage start time and duration. Only applies when modeling outages using the outage_start_time_steps, outage_durations, and outage_probabilities inputs, and do not apply when modeling a single outage using outage_start_time_step and outage_end_time_step.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000.0)]),
        ),
        migrations.AlterField(
            model_name='siteinputs',
            name='min_resil_time_steps',
            field=models.IntegerField(blank=True, help_text='The minimum number consecutive timesteps that load must be fully met once an outage begins. Only applies to multiple outage modeling using inputs outage_start_time_steps and outage_durations.', null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]