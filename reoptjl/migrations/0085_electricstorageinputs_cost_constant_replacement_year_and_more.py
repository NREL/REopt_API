# Generated by Django 4.0.7 on 2025-05-19 20:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reoptjl', '0084_merge_20250424_1814'),
    ]

    operations = [
        migrations.AddField(
            model_name='electricstorageinputs',
            name='cost_constant_replacement_year',
            field=models.IntegerField(blank=True, default=10, help_text='Number of years from start of analysis period to apply replace_cost_constant.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(75)]),
        ),
        migrations.AddField(
            model_name='electricstorageinputs',
            name='installed_cost_constant',
            field=models.FloatField(blank=True, default=0.0, help_text='Fixed upfront cost for battery installation, independent of size.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)]),
        ),
        migrations.AddField(
            model_name='electricstorageinputs',
            name='replace_cost_constant',
            field=models.FloatField(blank=True, default=0.0, help_text='Fixed replacement cost for battery, independent of size.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000.0)]),
        ),
    ]
