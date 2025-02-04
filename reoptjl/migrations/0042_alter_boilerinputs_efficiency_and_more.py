# Generated by Django 4.0.7 on 2023-09-12 22:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reoptjl', '0041_merge_20230901_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boilerinputs',
            name='efficiency',
            field=models.FloatField(blank=True, default=0.8, help_text='New boiler system efficiency - conversion of fuel to usable heating thermal energy.', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)]),
        ),
        migrations.AlterField(
            model_name='boilerinputs',
            name='max_mmbtu_per_hour',
            field=models.FloatField(blank=True, default=10000000.0, help_text='Maximum thermal power size', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100000000.0)]),
        ),
        migrations.AlterField(
            model_name='boilerinputs',
            name='min_mmbtu_per_hour',
            field=models.FloatField(blank=True, default=0.0, help_text='Minimum thermal power size', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100000000.0)]),
        ),
        migrations.AlterField(
            model_name='ghpinputs',
            name='building_sqft',
            field=models.FloatField(help_text='Building square footage for GHP/HVAC cost calculations', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100000000.0)]),
        ),
        migrations.AlterField(
            model_name='steamturbineinputs',
            name='can_curtail',
            field=models.BooleanField(blank=True, default=False, help_text='True/False for if technology has the ability to curtail energy production.', null=True),
        ),
        migrations.AlterField(
            model_name='steamturbineinputs',
            name='can_export_beyond_nem_limit',
            field=models.BooleanField(blank=True, default=False, help_text='True/False for if technology can export energy beyond the annual site load (and be compensated for that energy at the export_rate_beyond_net_metering_limit).Note that if off-grid is true, can_export_beyond_nem_limit is always set to False.', null=True),
        ),
        migrations.AlterField(
            model_name='steamturbineinputs',
            name='can_net_meter',
            field=models.BooleanField(blank=True, default=False, help_text='True/False for if technology has option to participate in net metering agreement with utility. Note that a technology can only participate in either net metering or wholesale rates (not both).Note that if off-grid is true, net metering is always set to False.', null=True),
        ),
        migrations.AlterField(
            model_name='steamturbineinputs',
            name='can_wholesale',
            field=models.BooleanField(blank=True, default=False, help_text='True/False for if technology has option to export energy that is compensated at the wholesale_rate. Note that a technology can only participate in either net metering or wholesale rates (not both).Note that if off-grid is true, can_wholesale is always set to False.', null=True),
        ),
        migrations.AlterField(
            model_name='steamturbineinputs',
            name='inlet_steam_superheat_degF',
            field=models.FloatField(blank=True, default=0.0, help_text='Alternative input to inlet steam temperature, this is the superheat amount (delta from T_saturation) to the steam turbine', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(700.0)]),
        ),
        migrations.AlterField(
            model_name='steamturbineinputs',
            name='is_condensing',
            field=models.BooleanField(blank=True, default=False, help_text='Steam turbine type, if it is a condensing turbine which produces no useful thermal (max electric output)', null=True),
        ),
        migrations.AlterField(
            model_name='steamturbineinputs',
            name='macrs_bonus_fraction',
            field=models.FloatField(blank=True, default=1.0, help_text='Percent of upfront project costs to depreciate in year one in addition to scheduled depreciation', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='steamturbineinputs',
            name='macrs_option_years',
            field=models.IntegerField(blank=True, choices=[(0, 'Zero'), (5, 'Five'), (7, 'Seven')], default=0, help_text='Duration over which accelerated depreciation will occur. Set to zero to disable', null=True),
        ),
        migrations.AlterField(
            model_name='steamturbineinputs',
            name='max_kw',
            field=models.FloatField(blank=True, default=100000000.0, help_text='Maximum steam turbine size constraint for optimization', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)]),
        ),
        migrations.AlterField(
            model_name='steamturbineinputs',
            name='min_kw',
            field=models.FloatField(blank=True, default=0.0, help_text='Minimum steam turbine size constraint for optimization', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)]),
        ),
        migrations.AlterField(
            model_name='steamturbineinputs',
            name='om_cost_per_kw',
            field=models.FloatField(blank=True, default=0.0, help_text='Annual steam turbine fixed operations and maintenance costs in $/kW', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5000.0)]),
        ),
        migrations.AlterField(
            model_name='steamturbineinputs',
            name='outlet_steam_min_vapor_fraction',
            field=models.FloatField(blank=True, default=0.8, help_text='Minimum practical vapor fraction of steam at the exit of the steam turbine', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)]),
        ),
    ]
