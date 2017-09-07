# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-06 21:13
from __future__ import unicode_literals

from django.db import migrations, models
import weights.models


class Migration(migrations.Migration):

    dependencies = [
        ('weights', '0011_measure_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='pigeonuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to=weights.models.get_avatar_path),
        ),
        migrations.AddField(
            model_name='pigeonuser',
            name='nickname',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]