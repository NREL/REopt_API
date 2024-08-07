# Generated by Django 3.1.12 on 2021-07-15 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0116_auto_20210715_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialmodel',
            name='nox_cost_us_dollars_per_tonne',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='financialmodel',
            name='pm_cost_us_dollars_per_tonne',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='financialmodel',
            name='so2_cost_us_dollars_per_tonne',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scenariomodel',
            name='include_health_in_objective',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
