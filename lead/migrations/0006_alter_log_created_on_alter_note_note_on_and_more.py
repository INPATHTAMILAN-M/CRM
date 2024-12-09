# Generated by Django 5.1.2 on 2024-10-17 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0005_alter_contact_created_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='created_on',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='note_on',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='created_on',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='created_on',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='task_assignment',
            name='assigned_on',
            field=models.DateField(auto_now_add=True),
        ),
    ]
