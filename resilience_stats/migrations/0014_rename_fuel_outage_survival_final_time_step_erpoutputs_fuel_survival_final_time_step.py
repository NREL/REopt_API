# Generated by Django 4.0.4 on 2023-09-20 05:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resilience_stats', '0013_alter_erpelectricstorageinputs_num_battery_bins'),
    ]

    operations = [
        migrations.RenameField(
            model_name='erpoutputs',
            old_name='fuel_outage_survival_final_time_step',
            new_name='fuel_survival_final_time_step',
        ),
    ]
