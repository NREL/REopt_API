# Generated by Django 3.1.13 on 2021-11-02 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0121_auto_20211012_0305'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadprofilemodel',
            name='load_met_pct',
            field=models.FloatField(blank=True, null=True),
        ),
    ]