# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=512)),
                ('body', models.TextField()),
                ('date', models.DateTimeField(null=True, verbose_name=b'posted', blank=True)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name=b'modified')),
                ('draft', models.BooleanField(default=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
