# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-24 03:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0025_auto_20190325_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='upload_file_temp',
            name='remark',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]