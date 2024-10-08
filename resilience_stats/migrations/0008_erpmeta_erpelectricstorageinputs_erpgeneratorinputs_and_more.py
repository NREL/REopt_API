# Generated by Django 4.0.4 on 2023-01-05 17:45

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import resilience_stats.models


class Migration(migrations.Migration):

    dependencies = [
        ('resilience_stats', '0007_resiliencemodel_avoided_outage_costs_us_dollars'),
    ]

    operations = [
        migrations.CreateModel(
            name='ERPMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_uuid', models.UUIDField(unique=True)),
                ('user_uuid', models.TextField(blank=True, default='', help_text='The assigned unique ID of a signed in REopt user.')),
                ('reopt_run_uuid', models.UUIDField(blank=True, help_text='The unique ID of a REopt optimization run from which to load inputs.', null=True)),
                ('job_type', models.TextField(default='developer.nrel.gov')),
                ('status', models.TextField(blank=True, default='', help_text='Status of the ERP job.')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('reopt_version', models.TextField(blank=True, default='', help_text='Version number of the REopt Julia package that is used to calculate reliability.')),
            ],
            bases=(resilience_stats.models.BaseModel, models.Model),
        ),
        migrations.CreateModel(
            name='ERPElectricStorageInputs',
            fields=[
                ('meta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='ERPElectricStorageInputs', serialize=False, to='resilience_stats.erpmeta')),
                ('operational_availability', models.FloatField(blank=True, default=1.0, help_text='Fraction of year battery system not down for maintenance', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)])),
                ('size_kw', models.FloatField(blank=True, default=0.0, help_text='Battery kW power capacity', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)])),
                ('size_kwh', models.FloatField(blank=True, default=0.0, help_text='Battery kWh energy capacity', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)])),
                ('starting_soc_series_fraction', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(validators=[django.core.validators.MinValueValidator(0)]), blank=True, default=list, help_text='Battery state of charge fraction when an outage begins, at each timestep. Must be hourly (8,760 samples).', size=None)),
                ('charge_efficiency', models.FloatField(blank=True, default=0.948, help_text='Efficiency of charging battery', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('discharge_efficiency', models.FloatField(blank=True, default=0.948, help_text='Efficiency of discharging battery', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('num_battery_bins', models.IntegerField(blank=True, default=100, help_text='Number of bins for modeling battery state of charge', validators=[django.core.validators.MinValueValidator(1)])),
            ],
            bases=(resilience_stats.models.BaseModel, models.Model),
        ),
        migrations.CreateModel(
            name='ERPGeneratorInputs',
            fields=[
                ('meta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='ERPGeneratorInputs', serialize=False, to='resilience_stats.erpmeta')),
                ('operational_availability', models.FloatField(blank=True, default=0.995, help_text='Fraction of year generators not down for maintenance', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('failure_to_start', models.FloatField(blank=True, default=0.0094, help_text='Chance of generator not starting when an outage occurs', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('mean_time_to_failure', models.FloatField(blank=True, default=1100, help_text="Average number of time steps between a generator's failures. 1/(failure to run probability).", validators=[django.core.validators.MinValueValidator(1)])),
                ('num_generators', models.IntegerField(blank=True, default=1, help_text='Number of generator units', validators=[django.core.validators.MinValueValidator(1)])),
                ('size_kw', models.FloatField(blank=True, default=0.0, help_text='Generator unit capacity', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)])),
                ('fuel_avail_gal', models.FloatField(blank=True, default=1000000000.0, help_text='Amount of diesel fuel available, either for all generators or per generator depending on value of fuel_avail_gal_is_per_generator.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)])),
                ('fuel_avail_gal_is_per_generator', models.BooleanField(blank=True, default=False, help_text='Whether fuel_avail_gal is per generator or per generator type')),
                ('electric_efficiency_half_load', models.FloatField(blank=True, help_text='Electric efficiency of generator running at half load.electric_efficiency_full_load', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)])),
                ('electric_efficiency_full_load', models.FloatField(blank=True, default=0.34, help_text='Electric efficiency of generator running at full load.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)])),
            ],
            bases=(resilience_stats.models.BaseModel, models.Model),
        ),
        migrations.CreateModel(
            name='ERPOutageInputs',
            fields=[
                ('meta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='ERPOutageInputs', serialize=False, to='resilience_stats.erpmeta')),
                ('max_outage_duration', models.IntegerField(blank=True, default=336, help_text='Maximum outage duration modeled', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(672)])),
                ('critical_loads_kw', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), help_text='Critical load during an outage. Must be hourly (8,760 samples). All non-net load values must be greater than or equal to zero.', size=None)),
            ],
            bases=(resilience_stats.models.BaseModel, models.Model),
        ),
        migrations.CreateModel(
            name='ERPOutputs',
            fields=[
                ('meta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='ERPOutputs', serialize=False, to='resilience_stats.erpmeta')),
                ('unlimited_fuel_mean_cumulative_survival_by_duration', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='The mean, calculated over outages starting at each hour of the year, of the probability of surviving up to and including each hour of max_outage_duration, if generator fuel is unlimited.', size=None)),
                ('unlimited_fuel_min_cumulative_survival_by_duration', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='The minimum, calculated over outages starting at each hour of the year, of the probability of surviving up to and including each hour of max_outage_duration, if generator fuel is unlimited.', size=None)),
                ('unlimited_fuel_cumulative_survival_final_time_step', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='The probability of surviving the full max_outage_duration, for outages starting at each hour of the year, if generator fuel is unlimited.', size=None)),
                ('mean_fuel_survival_by_duration', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='The probability, averaged over outages starting at each hour of the year, of having sufficient fuel to survive up to and including each hour of max_outage_duration.', size=None)),
                ('fuel_outage_survival_final_time_step', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, help_text='Whether there is sufficient fuel to survive the full max_outage_duration, for outages starting at each hour of the year. A 1 means true, a 0 means false.', size=None)),
                ('mean_cumulative_survival_by_duration', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='The mean, calculated over outages starting at each hour of the year, of the probability of surviving up to and including each hour of max_outage_duration.', size=None)),
                ('min_cumulative_survival_by_duration', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='The minimum, calculated over outages starting at each hour of the year, of the probability of surviving up to and including each hour of max_outage_duration.', size=None)),
                ('cumulative_survival_final_time_step', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='The probability of surviving the full max_outage_duration, for outages starting at each hour of the year.', size=None)),
                ('mean_cumulative_survival_final_time_step', models.FloatField(blank=True, help_text='The mean, calculated over outages starting at each hour of the year, of the probability of surviving the full max_outage_duration.', null=True)),
                ('monthly_min_cumulative_survival_final_time_step', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='The monthly minimums, calculated over outages starting at each hour of the month, of the probability of surviving the full max_outage_duration.', size=None)),
                ('monthly_lower_quartile_cumulative_survival_final_time_step', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='The monthly lower quartile cutoff, calculated over outages starting at each hour of the month, of the probability of surviving the full max_outage_duration.', size=None)),
                ('monthly_median_cumulative_survival_final_time_step', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='The monthly medians, calculated over outages starting at each hour of the month, of the probability of surviving the full max_outage_duration.', size=None)),
                ('monthly_upper_quartile_cumulative_survival_final_time_step', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='The monthly upper quartile cutoff, calculated over outages starting at each hour of the month, of the probability of surviving the full max_outage_duration.', size=None)),
                ('monthly_max_cumulative_survival_final_time_step', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='The monthly maximums, calculated over outages starting at each hour of the month, of the probability of surviving the full max_outage_duration.', size=None)),
            ],
            bases=(resilience_stats.models.BaseModel, models.Model),
        ),
        migrations.CreateModel(
            name='ERPPrimeGeneratorInputs',
            fields=[
                ('meta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='ERPPrimeGeneratorInputs', serialize=False, to='resilience_stats.erpmeta')),
                ('is_chp', models.BooleanField(blank=True, default=False, help_text='Whether prime generator system is CHP')),
                ('prime_mover', models.TextField(choices=[('recip_engine', 'Recip Engine'), ('micro_turbine', 'Micro Turbine'), ('combustion_turbine', 'Combustion Turbine'), ('fuel_cell', 'Fuel Cell')], default='recip_engine', help_text='Prime generator/CHP prime mover, one of recip_engine, micro_turbine, combustion_turbine, fuel_cell')),
                ('operational_availability', models.FloatField(blank=True, help_text='Fraction of year prime generator/CHP units are not down for maintenance', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('failure_to_start', models.FloatField(blank=True, default=0, help_text='Chance of prime generator/CHP unit not starting when an outage occurs', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('mean_time_to_failure', models.FloatField(blank=True, help_text="Average number of time steps between a prime generator/CHP unit's failures. 1/(failure to run probability).", null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('num_generators', models.IntegerField(blank=True, default=1, help_text='Number of prime generator/CHP units', validators=[django.core.validators.MinValueValidator(1)])),
                ('size_kw', models.FloatField(blank=True, default=0.0, help_text='Prime generator/CHP unit electric capacity', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)])),
                ('electric_efficiency_half_load', models.FloatField(blank=True, help_text='Electric efficiency of prime generator/CHP unit running at half load.electric_efficiency_full_load', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)])),
                ('electric_efficiency_full_load', models.FloatField(default=0.34, help_text='Electric efficiency of prime generator/CHP unit running at full load.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)])),
            ],
            bases=(resilience_stats.models.BaseModel, models.Model),
        ),
        migrations.CreateModel(
            name='ERPPVInputs',
            fields=[
                ('meta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='ERPPVInputs', serialize=False, to='resilience_stats.erpmeta')),
                ('operational_availability', models.FloatField(blank=True, default=1.0, help_text='Fraction of year PV system not down for maintenance', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)])),
                ('size_kw', models.FloatField(blank=True, default=0.0, help_text='PV system capacity', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)])),
                ('production_factor_series', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]), blank=True, default=list, help_text='PV system output at each timestep, normalized to PV system size. Must be hourly (8,760 samples).', size=None)),
            ],
            bases=(resilience_stats.models.BaseModel, models.Model),
        ),
    ]
