# Generated by Django 5.1.2 on 2025-01-04 07:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lead", "0044_alter_opportunity_currency_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="task_date_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
