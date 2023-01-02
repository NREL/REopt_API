# Generated by Django 4.0.4 on 2022-12-22 18:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resilience_stats', '0010_erpprimegeneratorinputs_prime_mover_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='erpoutputs',
            old_name='cumulative_outage_survival_final_time_step',
            new_name='cumulative_survival_final_time_step',
        ),
        migrations.RenameField(
            model_name='erpoutputs',
            old_name='mean_cumulative_outage_survival_final_time_step',
            new_name='mean_cumulative_survival_final_time_step',
        ),
        migrations.RenameField(
            model_name='erpoutputs',
            old_name='monthly_cumulative_outage_survival_final_time_step',
            new_name='monthly_cumulative_survival_final_time_step',
        ),
        migrations.RenameField(
            model_name='erpoutputs',
            old_name='unlimited_fuel_cumulative_outage_survival_final_time_step',
            new_name='unlimited_fuel_cumulative_survival_final_time_step',
        ),
        migrations.RemoveField(
            model_name='erpgeneratorinputs',
            name='failure_to_run',
        ),
        migrations.RemoveField(
            model_name='erpprimegeneratorinputs',
            name='failure_to_run',
        ),
        migrations.AddField(
            model_name='erpgeneratorinputs',
            name='mean_time_to_failure',
            field=models.FloatField(blank=True, default=637, help_text="Average number of time steps between a generator's failures. 1/(failure to run probability).", validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='erpprimegeneratorinputs',
            name='mean_time_to_failure',
            field=models.FloatField(blank=True, help_text="Average number of time steps between a prime generator/CHP unit's failures. 1/(failure to run probability).", null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='erpprimegeneratorinputs',
            name='electric_efficiency_full_load',
            field=models.FloatField(default=0.34, help_text='Electric efficiency of prime generator/CHP unit running at full load.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)]),
        ),
        migrations.AlterField(
            model_name='erpprimegeneratorinputs',
            name='electric_efficiency_half_load',
            field=models.FloatField(blank=True, help_text='Electric efficiency of prime generator/CHP unit running at half load.electric_efficiency_full_load', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)]),
        ),
        migrations.AlterField(
            model_name='erpprimegeneratorinputs',
            name='failure_to_start',
            field=models.FloatField(blank=True, default=0, help_text='Chance of prime generator/CHP unit not starting when an outage occurs', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='erpprimegeneratorinputs',
            name='num_generators',
            field=models.IntegerField(blank=True, default=1, help_text='Number of prime generator/CHP units', validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='erpprimegeneratorinputs',
            name='operational_availability',
            field=models.FloatField(blank=True, help_text='Fraction of year prime generator/CHP units are not down for maintenance', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='erpprimegeneratorinputs',
            name='size_kw',
            field=models.FloatField(blank=True, default=0.0, help_text='Prime generator/CHP unit electric capacity', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)]),
        ),
    ]