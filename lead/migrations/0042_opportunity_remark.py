# Generated by Django 5.1.2 on 2025-01-03 06:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lead", "0041_contact_lead_source_from"),
    ]

    operations = [
        migrations.AddField(
            model_name="opportunity",
            name="remark",
            field=models.TextField(blank=True, null=True),
        ),
    ]
