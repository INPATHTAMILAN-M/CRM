# Generated by Django 5.1.2 on 2024-12-10 09:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0025_alter_log_contact_alter_log_logtype_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='contact',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='lead.contact'),
            preserve_default=False,
        ),
    ]
