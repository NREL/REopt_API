# Generated by Django 4.0.7 on 2025-02-05 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reoptjl', '0078_merge_20250128_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteinputs',
            name='include_grid_renewable_fraction_in_RE_constraints',
            field=models.BooleanField(blank=True, default=False, help_text='If True, then the renewable energy content of energy from the grid is included in any min or max renewable energy requirements.'),
        ),
        migrations.AlterField(
            model_name='siteoutputs',
            name='onsite_and_grid_renewable_electricity_fraction_of_elec_load_bau',
            field=models.FloatField(blank=True, help_text='Calculation is the same as onsite_renewable_electricity_fraction_of_elec_load_bau, but additionally includes the renewable energycontent of grid-purchased electricity, accounting for any battery efficiency losses.', null=True),
        ),
        migrations.AlterField(
            model_name='siteoutputs',
            name='onsite_and_grid_renewable_energy_fraction_of_total_load_bau',
            field=models.FloatField(blank=True, help_text='Calculation is the same as onsite_renewable_energy_fraction_of_total_load_bau, but additionally includes the renewable energycontent of grid-purchased electricity, accounting for any battery efficiency losses.', null=True),
        ),
    ]
