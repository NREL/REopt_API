# Generated by Django 4.0.7 on 2024-10-29 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reoptjl', '0073_domestichotwaterloadinputs_year_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domestichotwaterloadinputs',
            name='normalize_and_scale_load_profile_input',
            field=models.BooleanField(blank=True, default=False, help_text='Takes the input fuel_loads_mmbtu_per_hour and normalizes and scales it to annual or monthly energy inputs.'),
        ),
        migrations.AlterField(
            model_name='electricloadinputs',
            name='normalize_and_scale_load_profile_input',
            field=models.BooleanField(blank=True, default=False, help_text='Takes the input loads_kw and normalizes and scales it to annual or monthly energy inputs.'),
        ),
        migrations.AlterField(
            model_name='processheatloadinputs',
            name='normalize_and_scale_load_profile_input',
            field=models.BooleanField(blank=True, default=False, help_text='Takes the input fuel_loads_mmbtu_per_hour and normalizes and scales it to annual or monthly energy inputs.'),
        ),
        migrations.AlterField(
            model_name='spaceheatingloadinputs',
            name='normalize_and_scale_load_profile_input',
            field=models.BooleanField(blank=True, default=False, help_text='Takes the input fuel_loads_mmbtu_per_hour and normalizes and scales it to annual or monthly energy inputs.'),
        ),
    ]