# Generated by Django 3.1.8 on 2021-05-24 17:29

from django.db import migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0109_ghpmodel_ghpghx_inputs'),
    ]

    operations = [
        migrations.AddField(
            model_name='ghpmodel',
            name='ghpghx_chosen_outputs',
            field=picklefield.fields.PickledObjectField(editable=False, null=True),
        ),
    ]