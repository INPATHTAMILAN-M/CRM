# Generated by Django 5.1.2 on 2025-04-05 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0096_alter_contact_created_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='created_on',
            field=models.DateField(auto_now_add=True),
        ),
    ]
