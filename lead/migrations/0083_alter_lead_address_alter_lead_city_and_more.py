# Generated by Django 5.1.2 on 2025-03-07 06:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_stage_probability'),
        ('lead', '0082_contact_secondary_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='lead',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.city'),
        ),
        migrations.AlterField(
            model_name='lead',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.country'),
        ),
        migrations.AlterField(
            model_name='lead',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.state'),
        ),
    ]
