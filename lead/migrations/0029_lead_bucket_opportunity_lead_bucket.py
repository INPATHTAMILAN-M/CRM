# Generated by Django 5.1.2 on 2024-12-11 06:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0028_alter_opportunity_lead'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lead_Bucket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='opportunity',
            name='lead_bucket',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lead.lead_bucket'),
        ),
    ]
