# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-20 09:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0013_customer_customer_wk_upload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='customer_wk_upload',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]
