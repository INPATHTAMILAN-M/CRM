# Generated by Django 5.1.2 on 2025-01-18 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_teams_bde_user_teams_bde_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stage',
            name='probability',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
