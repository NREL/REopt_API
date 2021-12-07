# Generated by Django 3.1.13 on 2021-12-02 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0140_merge_20211116_2116'),
    ]

    operations = [
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_gross_tCO2',
            new_name='lifecycle_emissions_tCO2',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_gross_tCO2_bau',
            new_name='lifecycle_emissions_tCO2_bau',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_gross_tNOx',
            new_name='lifecycle_emissions_tNOx',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_gross_tNOx_bau',
            new_name='lifecycle_emissions_tNOx_bau',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_gross_tPM25',
            new_name='lifecycle_emissions_tPM25',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_gross_tPM25_bau',
            new_name='lifecycle_emissions_tPM25_bau',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_gross_tSO2',
            new_name='lifecycle_emissions_tSO2',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_gross_tSO2_bau',
            new_name='lifecycle_emissions_tSO2_bau',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_net_if_selected_tCO2',
            new_name='year_one_emissions_tCO2',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_net_if_selected_tCO2_bau',
            new_name='year_one_emissions_tCO2_bau',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_net_if_selected_tNOx',
            new_name='year_one_emissions_tNOx',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_net_if_selected_tNOx_bau',
            new_name='year_one_emissions_tNOx_bau',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_net_if_selected_tPM25',
            new_name='year_one_emissions_tPM25',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_net_if_selected_tPM25_bau',
            new_name='year_one_emissions_tPM25_bau',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_net_if_selected_tSO2',
            new_name='year_one_emissions_tSO2',
        ),
        migrations.RenameField(
            model_name='electrictariffmodel',
            old_name='lifecycle_emissions_net_if_selected_tSO2_bau',
            new_name='year_one_emissions_tSO2_bau',
        ),
        migrations.RenameField(
            model_name='newboilermodel',
            old_name='year_one_emissions_lb_C02',
            new_name='emissions_factor_lb_NOx_per_mmbtu',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='lifecycle_emissions_tCO2',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='lifecycle_emissions_tCO2_bau',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='lifecycle_emissions_tNOx',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='lifecycle_emissions_tNOx_bau',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='lifecycle_emissions_tPM25',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='lifecycle_emissions_tPM25_bau',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='lifecycle_emissions_tSO2',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='lifecycle_emissions_tSO2_bau',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='year_one_emissions_tCO2',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='year_one_emissions_tCO2_bau',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='year_one_emissions_tNOx',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='year_one_emissions_tNOx_bau',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='year_one_emissions_tPM25',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='year_one_emissions_tPM25_bau',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='year_one_emissions_tSO2',
        ),
        migrations.RemoveField(
            model_name='boilermodel',
            name='year_one_emissions_tSO2_bau',
        ),
        migrations.RemoveField(
            model_name='chpmodel',
            name='lifecycle_emissions_tCO2',
        ),
        migrations.RemoveField(
            model_name='chpmodel',
            name='lifecycle_emissions_tNOx',
        ),
        migrations.RemoveField(
            model_name='chpmodel',
            name='lifecycle_emissions_tPM25',
        ),
        migrations.RemoveField(
            model_name='chpmodel',
            name='lifecycle_emissions_tSO2',
        ),
        migrations.RemoveField(
            model_name='chpmodel',
            name='year_one_emissions_tCO2',
        ),
        migrations.RemoveField(
            model_name='chpmodel',
            name='year_one_emissions_tNOx',
        ),
        migrations.RemoveField(
            model_name='chpmodel',
            name='year_one_emissions_tPM25',
        ),
        migrations.RemoveField(
            model_name='chpmodel',
            name='year_one_emissions_tSO2',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='lifecycle_emissions_offset_from_elec_exports_tCO2',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='lifecycle_emissions_offset_from_elec_exports_tCO2_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='lifecycle_emissions_offset_from_elec_exports_tNOx',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='lifecycle_emissions_offset_from_elec_exports_tNOx_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='lifecycle_emissions_offset_from_elec_exports_tPM25',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='lifecycle_emissions_offset_from_elec_exports_tPM25_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='lifecycle_emissions_offset_from_elec_exports_tSO2',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='lifecycle_emissions_offset_from_elec_exports_tSO2_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_gross_tCO2',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_gross_tCO2_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_gross_tNOx',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_gross_tNOx_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_gross_tPM25',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_gross_tPM25_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_gross_tSO2',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_gross_tSO2_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_net_if_selected_tCO2',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_net_if_selected_tCO2_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_net_if_selected_tNOx',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_net_if_selected_tNOx_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_net_if_selected_tPM25',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_net_if_selected_tPM25_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_net_if_selected_tSO2',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_net_if_selected_tSO2_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_offset_from_elec_exports_tCO2',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_offset_from_elec_exports_tCO2_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_offset_from_elec_exports_tNOx',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_offset_from_elec_exports_tNOx_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_offset_from_elec_exports_tPM25',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_offset_from_elec_exports_tPM25_bau',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_offset_from_elec_exports_tSO2',
        ),
        migrations.RemoveField(
            model_name='electrictariffmodel',
            name='year_one_emissions_offset_from_elec_exports_tSO2_bau',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='lifecycle_emissions_tCO2',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='lifecycle_emissions_tCO2_bau',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='lifecycle_emissions_tNOx',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='lifecycle_emissions_tNOx_bau',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='lifecycle_emissions_tPM25',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='lifecycle_emissions_tPM25_bau',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='lifecycle_emissions_tSO2',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='lifecycle_emissions_tSO2_bau',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='year_one_emissions_tCO2',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='year_one_emissions_tCO2_bau',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='year_one_emissions_tNOx',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='year_one_emissions_tNOx_bau',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='year_one_emissions_tPM25',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='year_one_emissions_tPM25_bau',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='year_one_emissions_tSO2',
        ),
        migrations.RemoveField(
            model_name='generatormodel',
            name='year_one_emissions_tSO2_bau',
        ),
        migrations.AddField(
            model_name='fueltariffmodel',
            name='newboiler_fuel_percent_RE',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='newboilermodel',
            name='emissions_factor_lb_PM25_per_mmbtu',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='newboilermodel',
            name='emissions_factor_lb_SO2_per_mmbtu',
            field=models.FloatField(blank=True, null=True),
        ),
    ]