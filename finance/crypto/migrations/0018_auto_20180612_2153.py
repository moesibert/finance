# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-06-12 19:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0017_asset_acc_movie'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='acc_movie',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='undefined', to='crypto.Movie'),
        ),
    ]
