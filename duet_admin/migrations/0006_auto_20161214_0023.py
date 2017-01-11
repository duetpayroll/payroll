# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-12-13 18:23
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('duet_admin', '0005_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 12, 13, 18, 23, 47, 341224, tzinfo=utc), verbose_name='Created At'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='settings',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 12, 13, 18, 23, 51, 710474, tzinfo=utc), verbose_name='Modified At'),
            preserve_default=False,
        ),
    ]