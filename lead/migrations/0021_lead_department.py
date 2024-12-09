# Generated by Django 5.1.2 on 2024-12-09 10:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lead", "0020_remove_contact_lead_source_lead_lead_source_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="lead",
            name="department",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="lead.department",
            ),
        ),
    ]