# Generated by Django 4.0.4 on 2023-03-07 22:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resilience_stats', '0009_erpelectricstorageinputs_minimum_soc_fraction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='erpelectricstorageinputs',
            name='operational_availability',
            field=models.FloatField(blank=True, default=0.97, help_text='Fraction of year battery system not down for maintenance', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)]),
        ),
        migrations.AlterField(
            model_name='erppvinputs',
            name='operational_availability',
            field=models.FloatField(blank=True, default=0.98, help_text='Fraction of year PV system not down for maintenance', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)]),
        ),
    ]
