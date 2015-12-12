# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def slug_posts(apps, schema_editor):
    BlogPost = apps.get_model("blog", "BlogPost")
    for post in BlogPost.objects.all():
        post.slug = str(post.id)
        post.save()


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_blogpost_slug'),
    ]

    operations = [
        migrations.RunPython(slug_posts, reverse_code=migrations.RunPython.noop),
    ]
