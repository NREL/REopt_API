# Generated by Django 3.1.8 on 2021-05-20 21:03

import django.contrib.postgres.fields
from django.db import migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0108_ghpmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='ghpmodel',
            name='ghpghx_inputs',
            field=django.contrib.postgres.fields.ArrayField(base_field=picklefield.fields.PickledObjectField(editable=False, null=True), null=True, size=None),
        ),
    ]