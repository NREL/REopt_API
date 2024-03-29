# Generated by Django 4.0.4 on 2023-01-07 21:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resilience_stats', '0008_erpmeta_erpelectricstorageinputs_erpgeneratorinputs_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='erpelectricstorageinputs',
            name='minimum_soc_fraction',
            field=models.FloatField(blank=True, default=0.0, help_text='Minimum battery state of charge allowed during an outage', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
    ]
