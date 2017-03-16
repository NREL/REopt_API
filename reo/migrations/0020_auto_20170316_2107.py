# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0019_auto_20170313_2244'),
    ]

    operations = [
        migrations.RenameField(
            model_name='runoutput',
            old_name='utility_kwh',
            new_name='year_one_utility_kwh',
        ),
        migrations.AddField(
            model_name='runoutput',
            name='average_yearly_pv_energy_produced',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='net_capital_costs_plus_om',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='total_demand_cost',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='total_energy_cost',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='total_payments_to_third_party_owner',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_demand_cost_bau',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_energy_cost_bau',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runoutput',
            name='year_one_payments_to_third_party_owner',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
