# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-20 09:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0012_auto_20190219_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='customer_wk_upload',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
