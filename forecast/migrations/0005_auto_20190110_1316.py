# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-10 06:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0004_auto_20190108_1536'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.CharField(blank=True, max_length=20, null=True)),
                ('customer_name', models.CharField(blank=True, max_length=125, null=True)),
                ('customer_initial', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.RenameField(
            model_name='user_forecast',
            old_name='customer',
            new_name='customer_list',
        ),
        migrations.AlterField(
            model_name='file_upload',
            name='customer',
            field=models.ForeignKey(blank=True, max_length=10, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Customer_upload', to='forecast.Customer'),
        ),
        migrations.AddField(
            model_name='forecast',
            name='customer',
            field=models.ForeignKey(blank=True, max_length=10, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Customer_forcast', to='forecast.Customer'),
        ),
    ]
