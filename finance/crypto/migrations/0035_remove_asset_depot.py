# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-06-25 10:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0034_auto_20180625_1215'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='depot',
        ),
    ]
