# Generated by Django 5.1.2 on 2024-12-07 06:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lead", "0013_lead_assinged_to_lead_lead_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="is_primary",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="log",
            name="lead",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="lead.lead",
            ),
        ),
        migrations.AddField(
            model_name="log",
            name="opportunity",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="lead.opportunity",
            ),
        ),
    ]
