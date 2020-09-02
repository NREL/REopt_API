
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reo', '0075_remove_loadprofilemodel_year_one_electric_load_series_kw_bau'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE reo_chpmodel ALTER COLUMN installed_cost_us_dollars_per_kw TYPE real USING installed_cost_us_dollars_per_kw::real;"),
        migrations.RunSQL(
            "ALTER TABLE reo_chpmodel ALTER COLUMN installed_cost_us_dollars_per_kw TYPE real[] USING array[installed_cost_us_dollars_per_kw], ALTER COLUMN installed_cost_us_dollars_per_kw SET DEFAULT '{}';"),
        migrations.AddField(
            model_name='chpmodel',
            name='tech_size_for_cost_curve',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, null=True),
                                                            default=list, size=None),
        ),
        migrations.AlterField(
            model_name='chpmodel',
            name='installed_cost_us_dollars_per_kw',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, null=True),
                                                            default=list, size=None),
        ),
    ]
