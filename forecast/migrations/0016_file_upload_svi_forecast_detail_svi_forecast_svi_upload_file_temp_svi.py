# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-03-15 04:08
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0015_forecast_detail_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='File_Upload_Svi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(blank=True, max_length=255, null=True)),
                ('file_path', models.FileField(blank=True, null=True, upload_to=b'')),
                ('upload_date', models.CharField(blank=True, max_length=25, null=True)),
                ('upload_week', models.CharField(blank=True, max_length=5, null=True)),
                ('customer', models.ForeignKey(blank=True, max_length=10, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Customer_upload_svi', to='forecast.Customer')),
                ('upload_by', models.ForeignKey(blank=True, max_length=10, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='User_Forecast_File_svi', to='forecast.User_Forecast')),
            ],
        ),
        migrations.CreateModel(
            name='Forecast_Detail_svi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('version', models.CharField(blank=True, max_length=25, null=True)),
                ('qty', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=20, null=True)),
                ('work_week', models.CharField(blank=True, max_length=20, null=True)),
                ('year', models.CharField(blank=True, max_length=4, null=True)),
                ('file_upload', models.ForeignKey(blank=True, max_length=10, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='File_Upload_forecast_svi', to='forecast.File_Upload')),
                ('forecast', models.ForeignKey(blank=True, max_length=10, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Forecast_detail_svi', to='forecast.Forecast')),
            ],
        ),
        migrations.CreateModel(
            name='Forecast_svi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(blank=True, max_length=20, null=True)),
                ('description', models.CharField(blank=True, max_length=1024, null=True)),
                ('first_demand_date', models.CharField(blank=True, max_length=25, null=True)),
                ('last_version', models.CharField(blank=True, max_length=25, null=True)),
                ('customer', models.ForeignKey(blank=True, max_length=10, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Customer_forcast_svi', to='forecast.Customer')),
                ('user', models.ForeignKey(blank=True, max_length=10, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='User_Forecast_Forecast_svi', to='forecast.User_Forecast')),
            ],
        ),
        migrations.CreateModel(
            name='Upload_file_temp_svi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_done', models.BooleanField(default=False)),
                ('file_upload', models.ForeignKey(blank=True, max_length=10, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='File_Upload_temp_svi', to='forecast.File_Upload')),
                ('user', models.ForeignKey(blank=True, max_length=10, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='User_Forecast_temp_svi', to='forecast.User_Forecast')),
            ],
        ),
    ]