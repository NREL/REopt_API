# Generated by Django 4.0.4 on 2022-06-29 18:21

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import job.models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0004_electricstorageoutputs_initial_capital_cost_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoilerInputs',
            fields=[
                ('meta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='BoilerInputs', serialize=False, to='job.apimeta')),
                ('min_mmbtu_per_hour', models.FloatField(blank=True, default=0.0, help_text='Minimum thermal power size', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1000000000.0)])),
                ('max_mmbtu_per_hour', models.FloatField(blank=True, default=0.0, help_text='Maximum thermal power size', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1000000000.0)])),
                ('efficiency', models.FloatField(blank=True, default=0.8, help_text='New boiler system efficiency - conversion of fuel to usable heating thermal energy.', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ('fuel_cost_per_mmbtu', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0)]), blank=True, default=list, help_text='Fuel cost in [$/MMBtu]', size=None)),
                ('macrs_option_years', models.IntegerField(blank=True, choices=[(0, 'Zero'), (5, 'Five'), (7, 'Seven')], default=0, help_text='Duration over which accelerated depreciation will occur. Set to zero to disable', null=True)),
                ('macrs_bonus_pct', models.FloatField(blank=True, default=0.0, help_text='Percent of upfront project costs to depreciate in year one in addition to scheduled depreciation', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('installed_cost_per_mmbtu_per_hour', models.FloatField(blank=True, default=293000.0, help_text='Thermal power-based cost', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)])),
                ('om_cost_per_mmbtu_per_hour', models.FloatField(blank=True, default=2930.0, help_text='Thermal power-based fixed O&M cost', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)])),
                ('om_cost_per_mmbtu', models.FloatField(blank=True, default=0.0, help_text='Thermal energy-based variable O&M cost', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)])),
                ('fuel_type', models.TextField(blank=True, choices=[('natural_gas', 'Natural Gas'), ('landfill_bio_gas', 'Landfill Bio Gas'), ('propane', 'Propane'), ('diesel_oil', 'Diesel Oil'), ('uranium', 'Uranium')], default='natural_gas', help_text='Existing boiler fuel type, one of natural_gas, landfill_bio_gas, propane, diesel_oil, uranium', null=True)),
                ('can_supply_steam_turbine', models.BooleanField(blank=True, default=True, help_text='If the boiler can supply steam to the steam turbine for electric production', null=True)),
            ],
            bases=(job.models.BaseModel, models.Model),
        ),
        migrations.CreateModel(
            name='BoilerOutputs',
            fields=[
                ('meta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='BoilerOutputs', serialize=False, to='job.apimeta')),
                ('year_one_fuel_consumption_mmbtu', models.FloatField(blank=True, null=True)),
                ('year_one_fuel_consumption_mmbtu_per_hour', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, null=True), default=list, size=None)),
                ('lifecycle_fuel_cost', models.FloatField(blank=True, null=True)),
                ('lifecycle_per_unit_prod_om_costs', models.FloatField(blank=True, null=True)),
                ('lifecycle_fuel_cost_bau', models.FloatField(blank=True, null=True)),
                ('year_one_thermal_production_mmbtu', models.FloatField(blank=True, null=True)),
                ('year_one_fuel_cost', models.FloatField(blank=True, null=True)),
                ('thermal_to_tes_series_mmbtu_per_hour', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, null=True), default=list, size=None)),
                ('year_one_thermal_production_mmbtu_per_hour', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, null=True), default=list, size=None)),
                ('year_one_thermal_to_load_series_mmbtu_per_hour', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, null=True), default=list, size=None)),
            ],
            bases=(job.models.BaseModel, models.Model),
        ),
        migrations.CreateModel(
            name='ExistingBoilerInputs',
            fields=[
                ('meta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='ExistingBoilerInputs', serialize=False, to='job.apimeta')),
                ('production_type', models.TextField(blank=True, choices=[('steam', 'Steam'), ('hot_water', 'Hot Water')], default='hot_water', help_text='Boiler thermal production type, hot water or steam')),
                ('max_thermal_factor_on_peak_load', models.FloatField(blank=True, default=1.25, help_text='Factor on peak thermal LOAD which the boiler can supply', null=True, validators=[django.core.validators.MinValueValidator(1.0), django.core.validators.MaxValueValidator(5.0)])),
                ('efficiency', models.FloatField(blank=True, default=0.0, help_text='Existing boiler system efficiency - conversion of fuel to usable heating thermal energy.', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ('fuel_cost_per_mmbtu', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0)]), blank=True, default=list, help_text='The ExistingBoiler default operating cost is zero. Please provide this field to include non-zero BAU heating costs.The `fuel_cost_per_mmbtu` can be a scalar, a list of 12 monthly values, or a time series of values for every time step.If a scalar or a vector of 12 values are provided, then the value is scaled up to 8760 values.If a vector of 8760, 17520, or 35040 values is provided, it is adjusted to match timesteps per hour in the optimization.', size=None)),
                ('fuel_type', models.TextField(blank=True, choices=[('natural_gas', 'Natural Gas'), ('landfill_bio_gas', 'Landfill Bio Gas'), ('propane', 'Propane'), ('diesel_oil', 'Diesel Oil')], default='natural_gas', help_text='Existing boiler fuel type, one of natural_gas, landfill_bio_gas, propane, diesel_oil')),
                ('can_supply_steam_turbine', models.BooleanField(blank=True, default=False, help_text='If the boiler can supply steam to the steam turbine for electric production', null=True)),
            ],
            bases=(job.models.BaseModel, models.Model),
        ),
        migrations.CreateModel(
            name='ExistingBoilerOutputs',
            fields=[
                ('meta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='ExistingBoilerOutputs', serialize=False, to='job.apimeta')),
                ('year_one_fuel_consumption_mmbtu', models.FloatField(blank=True, null=True)),
                ('year_one_fuel_consumption_mmbtu_per_hour', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, null=True), default=list, size=None)),
                ('lifecycle_fuel_cost', models.FloatField(blank=True, null=True)),
                ('lifecycle_fuel_cost_bau', models.FloatField(blank=True, null=True)),
                ('year_one_thermal_production_mmbtu', models.FloatField(blank=True, null=True)),
                ('year_one_fuel_cost', models.FloatField(blank=True, null=True)),
                ('thermal_to_tes_series_mmbtu_per_hour', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, null=True), default=list, size=None)),
                ('year_one_thermal_production_mmbtu_per_hour', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, null=True), default=list, size=None)),
                ('year_one_thermal_to_load_series_mmbtu_per_hour', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, null=True), default=list, size=None)),
            ],
            bases=(job.models.BaseModel, models.Model),
        ),
        migrations.CreateModel(
            name='SpaceHeatingLoadInputs',
            fields=[
                ('meta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='SpaceHeatingLoadInputs', serialize=False, to='job.apimeta')),
                ('annual_mmbtu', models.FloatField(blank=True, help_text="Annual site space heating consumption, used to scale simulated default building load profile for the site's climate zone [MMBtu]", null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100000000)])),
                ('doe_reference_name', models.TextField(blank=True, choices=[('FastFoodRest', 'Fastfoodrest'), ('FullServiceRest', 'Fullservicerest'), ('Hospital', 'Hospital'), ('LargeHotel', 'Largehotel'), ('LargeOffice', 'Largeoffice'), ('MediumOffice', 'Mediumoffice'), ('MidriseApartment', 'Midriseapartment'), ('Outpatient', 'Outpatient'), ('PrimarySchool', 'Primaryschool'), ('RetailStore', 'Retailstore'), ('SecondarySchool', 'Secondaryschool'), ('SmallHotel', 'Smallhotel'), ('SmallOffice', 'Smalloffice'), ('StripMall', 'Stripmall'), ('Supermarket', 'Supermarket'), ('Warehouse', 'Warehouse'), ('FlatLoad', 'Flatload'), ('FlatLoad_24_5', 'Flatload 24 5'), ('FlatLoad_16_7', 'Flatload 16 7'), ('FlatLoad_16_5', 'Flatload 16 5'), ('FlatLoad_8_7', 'Flatload 8 7'), ('FlatLoad_8_5', 'Flatload 8 5')], help_text='Simulated load profile from DOE Commercial Reference Buildings https://energy.gov/eere/buildings/commercial-reference-buildings')),
                ('monthly_mmbtu', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100000000.0)]), blank=True, default=list, help_text="Monthly site space heating energy consumption in [MMbtu], used to scale simulated default building load profile for the site's climate zone", size=None)),
                ('fuel_loads_mmbtu_per_hour', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True), blank=True, default=list, help_text='Typical load over all hours in one year. Must be hourly (8,760 samples), 30 minute (17,520 samples), or 15 minute (35,040 samples). All non-net load values must be greater than or equal to zero. ', size=None)),
                ('blended_doe_reference_names', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(blank=True, choices=[('FastFoodRest', 'Fastfoodrest'), ('FullServiceRest', 'Fullservicerest'), ('Hospital', 'Hospital'), ('LargeHotel', 'Largehotel'), ('LargeOffice', 'Largeoffice'), ('MediumOffice', 'Mediumoffice'), ('MidriseApartment', 'Midriseapartment'), ('Outpatient', 'Outpatient'), ('PrimarySchool', 'Primaryschool'), ('RetailStore', 'Retailstore'), ('SecondarySchool', 'Secondaryschool'), ('SmallHotel', 'Smallhotel'), ('SmallOffice', 'Smalloffice'), ('StripMall', 'Stripmall'), ('Supermarket', 'Supermarket'), ('Warehouse', 'Warehouse'), ('FlatLoad', 'Flatload'), ('FlatLoad_24_5', 'Flatload 24 5'), ('FlatLoad_16_7', 'Flatload 16 7'), ('FlatLoad_16_5', 'Flatload 16 5'), ('FlatLoad_8_7', 'Flatload 8 7'), ('FlatLoad_8_5', 'Flatload 8 5')]), blank=True, default=list, help_text='Used in concert with blended_doe_reference_percents to create a blended load profile from multiple DoE Commercial Reference Buildings.', size=None)),
                ('blended_doe_reference_percents', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)]), blank=True, default=list, help_text='Used in concert with blended_doe_reference_names to create a blended load profile from multiple DoE Commercial Reference Buildings. Must sum to 1.0.', size=None)),
            ],
            bases=(job.models.BaseModel, models.Model),
        ),
        migrations.AddField(
            model_name='financialoutputs',
            name='lifecycle_fuel_costs_after_tax',
            field=models.FloatField(blank=True, help_text='Life cycle fuel cost over analysis period after tax.', null=True),
        ),
    ]