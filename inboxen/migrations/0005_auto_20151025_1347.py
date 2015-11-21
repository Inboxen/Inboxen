# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def kill_liberations(apps, schema_editor):
    Liberation = apps.get_model("inboxen", "Liberation")
    Liberation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('inboxen', '0004_auto_20151025_1017'),
    ]

    operations = [
        migrations.RunPython(kill_liberations, reverse_code=kill_liberations),
    ]
