# Generated by Django 5.1.2 on 2025-01-22 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0056_alter_contact_email_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
