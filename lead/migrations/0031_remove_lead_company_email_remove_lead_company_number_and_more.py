# Generated by Django 5.1.2 on 2024-12-30 11:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lead", "0030_contact_is_archive_alter_contact_lead_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="lead",
            name="company_email",
        ),
        migrations.RemoveField(
            model_name="lead",
            name="company_number",
        ),
        migrations.AddField(
            model_name="contact",
            name="remark",
            field=models.TextField(blank=True, null=True),
        ),
    ]