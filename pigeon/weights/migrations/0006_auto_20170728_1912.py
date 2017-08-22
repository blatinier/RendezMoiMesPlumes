# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-28 19:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weights', '0005_measure'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measure',
            name='measured_weight',
            field=models.DecimalField(decimal_places=3, max_digits=12),
        ),
        migrations.AlterField(
            model_name='measure',
            name='package_weight',
            field=models.DecimalField(decimal_places=3, max_digits=12),
        ),
    ]
