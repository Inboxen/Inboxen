# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffProfile',
            fields=[
                ('public_name', models.CharField(help_text="Their name, as they're known to the public", max_length=1024)),
                ('bio', models.TextField(help_text='Tell us about this a member of staff. Rendered with Markdown')),
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TOS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('published', models.BooleanField(default=False)),
                ('text', models.TextField(help_text='Text of TOS, Rendered with Markdown')),
                ('diff', models.TextField()),
            ],
            options={
                'ordering': ['-last_modified'],
                'get_latest_by': 'last_modified',
            },
        ),
    ]
