# Generated by Django 3.1.7 on 2021-05-20 23:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0115_auto_20210520_2242'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pvmodel',
            old_name='pv_om_cost_us_dollars',
            new_name='total_fixed_om_cost_us_dollars',
        ),
    ]