# Generated by Django 4.0.7 on 2023-10-04 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reoptjl', '0047_existingboileroutputs_annual_thermal_production_mmbtu_bau_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='existingboileroutputs',
            name='annual_fuel_consumption_mmbtu_bau',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='existingchilleroutputs',
            name='annual_electric_consumption_kwh_bau',
            field=models.FloatField(blank=True, help_text='Annual chiller electric consumption for BAU case [kWh]', null=True),
        ),
        migrations.AddField(
            model_name='existingchilleroutputs',
            name='annual_thermal_production_tonhour_bau',
            field=models.FloatField(blank=True, help_text='Annual chiller thermal production for BAU case [Ton Hour]', null=True),
        ),
        migrations.AddField(
            model_name='financialoutputs',
            name='lifecycle_fuel_costs_after_tax_bau',
            field=models.FloatField(blank=True, help_text='Component of lifecycle costs (LCC). This value is the present value of all fuel costs over the analysis period, after tax in the BAU case.', null=True),
        ),
        migrations.AlterField(
            model_name='existingchilleroutputs',
            name='annual_thermal_production_tonhour',
            field=models.FloatField(blank=True, help_text='Annual chiller thermal production [Ton Hour]', null=True),
        ),
    ]