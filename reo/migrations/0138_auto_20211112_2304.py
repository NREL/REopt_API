# Generated by Django 3.1.12 on 2021-11-12 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0137_auto_20211112_0327'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitemodel',
            name='year_one_heat_load_mmbtu',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sitemodel',
            name='year_one_heat_load_mmbtu_bau',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
