# Generated by Django 4.0.7 on 2023-01-05 23:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reoptjl', '0018_rename_year_one_electric_production_series_kw_chpoutputs_electric_production_series_kw_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pvoutputs',
            old_name='production_curtailed_series_kw',
            new_name='electric_curtailed_series_kw',
        ),
        migrations.RenameField(
            model_name='windoutputs',
            old_name='production_curtailed_series_kw',
            new_name='electric_curtailed_series_kw',
        ),
    ]