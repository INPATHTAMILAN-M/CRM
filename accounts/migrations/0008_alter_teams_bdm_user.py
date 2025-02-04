# Generated by Django 5.1.2 on 2025-01-20 11:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0007_alter_stage_probability"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="teams",
            name="bdm_user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bdm_user",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
