# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-06-04 12:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0011_remove_intelligenttimespan_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='IntelligentTimespan',
            new_name='Timespan',
        ),
    ]