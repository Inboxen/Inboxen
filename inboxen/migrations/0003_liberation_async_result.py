# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inboxen', '0002_remove_liberation_async_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='liberation',
            name='async_result',
            field=models.UUIDField(null=True),
        ),
    ]
