# Generated by Django 4.0.4 on 2023-07-05 18:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reoptjl', '0037_alter_generatorinputs_installed_cost_per_kw'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generatorinputs',
            name='installed_cost_per_kw',
            field=models.FloatField(blank=True, help_text='Installed diesel generator cost in $/kW', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100000.0)]),
        ),
    ]
