# Generated by Django 5.1.2 on 2025-04-01 08:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0091_alter_contact_assignment_assigned_by_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Contact_Assignment',
        ),
    ]
