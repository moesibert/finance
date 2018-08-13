# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-13 11:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0021_auto_20180813_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='change',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='changes', to='banking.Category'),
        ),
    ]