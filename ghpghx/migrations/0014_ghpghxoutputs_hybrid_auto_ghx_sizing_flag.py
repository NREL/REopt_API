# Generated by Django 4.0.7 on 2023-09-28 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ghpghx', '0013_alter_ghpghxinputs_init_sizing_factor_ft_per_peak_ton'),
    ]

    operations = [
        migrations.AddField(
            model_name='ghpghxoutputs',
            name='hybrid_auto_ghx_sizing_flag',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
