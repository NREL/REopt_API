# Generated by Django 2.2.13 on 2021-03-09 23:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0107_auto_20210309_1606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='windmodel',
            name='sr_provided_series_kw',
        ),
        migrations.RemoveField(
            model_name='windmodel',
            name='sr_required_pct',
        ),
        migrations.RemoveField(
            model_name='windmodel',
            name='sr_required_series_kw',
        ),
    ]
