# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-11 04:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0005_auto_20190110_1316'),
    ]

    operations = [
        migrations.CreateModel(
            name='Upload_file_temp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_done', models.BooleanField(default=False)),
                ('file_upload', models.ForeignKey(blank=True, max_length=10, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='File_Upload_temp', to='forecast.File_Upload')),
            ],
        ),
        migrations.AddField(
            model_name='forecast_detail',
            name='status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
