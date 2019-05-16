# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import annoying.fields


class Migration(migrations.Migration):

    dependencies = [
        ('inboxen', '0003_liberation_async_result'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='liberation',
            name='data',
        ),
        migrations.RemoveField(
            model_name='liberation',
            name='size',
        ),
        migrations.AddField(
            model_name='liberation',
            name='_path',
            field=models.CharField(max_length=255, unique=True, null=True),
        ),
        migrations.AlterField(
            model_name='liberation',
            name='user',
            field=annoying.fields.AutoOneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
    ]
