# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-06-04 12:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0007_intelligenttimespan_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timespan',
            name='timespan',
        ),
        migrations.DeleteModel(
            name='Timespan',
        ),
    ]