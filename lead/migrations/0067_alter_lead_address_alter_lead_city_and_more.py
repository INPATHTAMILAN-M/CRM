# Generated by Django 5.1.2 on 2025-02-06 09:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_stage_probability'),
        ('lead', '0066_opportunity_status_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='address',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lead',
            name='city',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.city'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lead',
            name='focus_segment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.focus_segment'),
        ),
        migrations.AlterField(
            model_name='lead',
            name='market_segment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.market_segment'),
        ),
        migrations.AlterField(
            model_name='lead',
            name='state',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.state'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='name',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='lead.opportunity_name'),
            preserve_default=False,
        ),
    ]
