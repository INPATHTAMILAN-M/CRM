# Generated by Django 5.1.2 on 2025-04-01 08:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0090_alter_contact_assignment_contact'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact_assignment',
            name='assigned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_by_contacts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='contact_assignment',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_contacts', to=settings.AUTH_USER_MODEL),
        ),
    ]
