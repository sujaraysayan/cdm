# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-04 04:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0009_auto_20190116_1508'),
    ]

    operations = [
        migrations.CreateModel(
            name='Last_upload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_week', models.CharField(blank=True, max_length=25, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='file_upload',
            name='upload_week',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]