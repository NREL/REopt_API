# Generated by Django 4.0.7 on 2025-06-04 19:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reoptjl', '0089_alter_electricstorageinputs_installed_cost_per_kw_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='existingboilerinputs',
            name='installed_cost_dollars',
            field=models.FloatField(blank=True, default=0.0, help_text='Cost incurred in BAU scenario, as well as Optimal if needed still, in dollars', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100000000.0)]),
        ),
        migrations.AddField(
            model_name='existingboilerinputs',
            name='installed_cost_per_mmbtu_per_hour',
            field=models.FloatField(blank=True, default=0.0, help_text="Thermal power capacity-based cost incurred in BAU and only based on what's needed in Optimal scenario", null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100000000.0)]),
        ),
        migrations.AddField(
            model_name='existingboileroutputs',
            name='size_mmbtu_per_hour_bau',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='existingchillerinputs',
            name='installed_cost_dollars',
            field=models.FloatField(blank=True, default=0.0, help_text='Cost incurred in BAU scenario, as well as Optimal if needed still, in dollars', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100000000.0)]),
        ),
        migrations.AddField(
            model_name='existingchillerinputs',
            name='installed_cost_per_ton',
            field=models.FloatField(blank=True, default=0.0, help_text="Thermal power capacity-based cost incurred in BAU and only based on what's needed in Optimal scenario", null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100000000.0)]),
        ),
        migrations.AddField(
            model_name='existingchilleroutputs',
            name='size_ton',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='existingchilleroutputs',
            name='size_ton_bau',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
