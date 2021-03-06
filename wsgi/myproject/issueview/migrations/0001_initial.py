# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-12-02 11:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repository', models.CharField(max_length=100)),
                ('issueid', models.CharField(max_length=10)),
                ('title', models.TextField()),
                ('url', models.TextField()),
                ('created', models.CharField(max_length=50)),
                ('updated', models.CharField(max_length=50)),
                ('assigned', models.CharField(max_length=50)),
                ('release', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=50)),
                ('comments', models.TextField()),
                ('changed', models.BooleanField(default=False)),
            ],
        ),
    ]
