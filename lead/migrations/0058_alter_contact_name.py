# Generated by Django 5.1.2 on 2025-01-30 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0057_alter_contact_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
