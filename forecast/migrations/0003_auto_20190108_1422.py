# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-08 07:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0002_forecast_last_version'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user_forecast',
            old_name='firstnamee',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='user_forecast',
            old_name='lastnamee',
            new_name='lastname',
        ),
    ]
