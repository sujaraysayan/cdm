# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-03-15 08:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0016_file_upload_svi_forecast_detail_svi_forecast_svi_upload_file_temp_svi'),
    ]

    operations = [
        migrations.AddField(
            model_name='forecast_svi',
            name='customer_version',
            field=models.ForeignKey(blank=True, max_length=10, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='file_upload', to='forecast.File_Upload'),
        ),
    ]
