# Generated by Django 5.1.2 on 2025-02-20 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0076_alter_log_opportunity_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='opportunity',
            name='opportunity_keyword',
            field=models.TextField(blank=True, null=True),
        ),
    ]
