# Generated by Django 4.0.7 on 2023-03-08 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reoptjl', '0025_merge_20230202_1907'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserUnlinkedRuns',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_uuid', models.UUIDField(unique=True)),
                ('user_uuid', models.UUIDField()),
            ],
        ),
    ]
