# Generated by Django 5.1.2 on 2025-01-04 13:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lead", "0046_alter_contact_lead_alter_log_contact"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="log",
            name="logtype",
        ),
        migrations.AddField(
            model_name="log",
            name="lead_log_status",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="lead.lead_status",
            ),
        ),
    ]
