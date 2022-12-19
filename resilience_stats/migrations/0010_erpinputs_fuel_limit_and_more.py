# Generated by Django 4.0.4 on 2022-11-30 23:28

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import resilience_stats.models


class Migration(migrations.Migration):

    dependencies = [
        ('resilience_stats', '0009_erpinputs_battery_operational_availability_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='erpinputs',
            name='fuel_limit',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)]), blank=True, default=resilience_stats.models.ERPInputs.generator_size_kw_default, help_text='Amount of fuel available, by generator type, either per type or per generator depending on value of fuel_limit_is_per_generator.', size=None),
        ),
        migrations.AddField(
            model_name='erpinputs',
            name='fuel_limit_is_per_generator',
            field=models.BooleanField(blank=True, default=True, help_text='Whether fuel_limit is per generator or per generator type'),
        ),
        migrations.AddField(
            model_name='erpinputs',
            name='generator_burn_rate_fuel_per_kwh',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)]), blank=True, default=resilience_stats.models.ERPInputs.generator_size_kw_default, help_text='Amount of fuel used per kWh produced by each generator type.', size=None),
        ),
        migrations.AddField(
            model_name='erpinputs',
            name='generator_fuel_intercept',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)]), blank=True, default=resilience_stats.models.ERPInputs.generator_size_kw_default, help_text='Amount of fuel burned per time step by each generator type while idling.', size=None),
        ),
    ]