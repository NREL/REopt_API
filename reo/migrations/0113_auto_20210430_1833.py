# Generated by Django 3.1.7 on 2021-04-30 18:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0112_auto_20210427_2116'),
    ]

    operations = [
        migrations.RenameField(
            model_name='financialmodel',
            old_name='total_distribution_system_cost_us_dollars',
            new_name='additional_cap_costs_us_dollars',
        ),
        migrations.RenameField(
            model_name='financialmodel',
            old_name='labor_cost_us_dollars_per_year',
            new_name='other_annual_costs_us_dollars_per_year',
        ),
        migrations.RenameField(
            model_name='financialmodel',
            old_name='distribution_system_cost_us_dollars',
            new_name='other_capital_costs_us_dollars',
        ),
        migrations.RenameField(
            model_name='financialmodel',
            old_name='lc_labor_cost_us_dollars',
            new_name='total_annual_cost_us_dollars',
        ),
        migrations.RemoveField(
            model_name='financialmodel',
            name='land_lease_us_dollars_per_year',
        ),
        migrations.RemoveField(
            model_name='financialmodel',
            name='lc_land_lease_us_dollars',
        ),
        migrations.RemoveField(
            model_name='financialmodel',
            name='powerhouse_civil_cost_us_dollars_per_sqft',
        ),
        migrations.RemoveField(
            model_name='financialmodel',
            name='pre_operating_expenses_us_dollars',
        ),
        migrations.RemoveField(
            model_name='financialmodel',
            name='pre_operating_expenses_us_dollars_per_kw',
        ),
        migrations.RemoveField(
            model_name='financialmodel',
            name='powerhouse_civil_cost_us_dollars',
        ),
        migrations.RemoveField(
            model_name='storagemodel',
            name='battery_room_size_sqft_per_kwh',
        ),
        migrations.RemoveField(
            model_name='storagemodel',
            name='inverter_room_size_sqft',
        ),
    ]
