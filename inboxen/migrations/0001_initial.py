# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import bitfield.models
import django_extensions.db.fields
import mptt.fields
import inboxen.fields
from django.conf import settings
import django.db.models.deletion
import djorm_pgbytea.lobject
import annoying.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Body',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hashed', models.CharField(unique=True, max_length=80)),
                ('data', models.BinaryField(default=b'')),
                ('size', models.PositiveIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(unique=True, max_length=253)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('flags', bitfield.models.BitField((b'deleted', b'read', b'seen', b'important', b'view_all_headers'), default=0)),
                ('received_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Header',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordinal', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='HeaderData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hashed', models.CharField(unique=True, max_length=80)),
                ('data', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='HeaderName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=78)),
            ],
        ),
        migrations.CreateModel(
            name='Inbox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inbox', models.CharField(max_length=64)),
                ('created', models.DateTimeField(verbose_name=b'Created')),
                ('flags', bitfield.models.BitField((b'deleted', b'new', b'exclude_from_unified', b'disabled'), default=0)),
                ('description', models.CharField(max_length=256, null=True, blank=True)),
                ('domain', models.ForeignKey(to='inboxen.Domain', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'verbose_name_plural': 'Inboxes',
            },
        ),
        migrations.CreateModel(
            name='Liberation',
            fields=[
                ('user', inboxen.fields.DeferAutoOneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('flags', bitfield.models.BitField((b'running', b'errored'), default=0)),
                ('data', djorm_pgbytea.lobject.LargeObjectField(null=True)),
                ('content_type', models.PositiveSmallIntegerField(default=0)),
                ('async_result', django_extensions.db.fields.UUIDField(auto=False, null=True)),
                ('started', models.DateTimeField(null=True)),
                ('last_finished', models.DateTimeField(null=True)),
                ('size', models.PositiveIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PartList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('body', models.ForeignKey(to='inboxen.Body', on_delete=django.db.models.deletion.PROTECT)),
                ('email', models.ForeignKey(related_name='parts', to='inboxen.Email')),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='inboxen.PartList', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.IntegerField(help_text='Pool increase requested')),
                ('succeeded', models.NullBooleanField(default=None, help_text='has the request been accepted?', verbose_name=b'accepted')),
                ('date', models.DateTimeField(help_text='date requested', verbose_name=b'requested', auto_now_add=True)),
                ('date_decided', models.DateTimeField(help_text='date staff accepted/rejected request', null=True)),
                ('result', models.CharField(max_length=1024, null=True, verbose_name=b'comment', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Statistic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(verbose_name=b'date')),
                ('users', annoying.fields.JSONField()),
                ('emails', annoying.fields.JSONField()),
                ('inboxes', annoying.fields.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', annoying.fields.AutoOneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('pool_amount', models.IntegerField(default=500)),
                ('flags', bitfield.models.BitField((b'prefer_html_email', b'unified_has_new_messages', b'ask_images', b'display_images'), default=5)),
                ('prefered_domain', models.ForeignKey(blank=True, to='inboxen.Domain', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='request',
            name='authorizer',
            field=models.ForeignKey(related_name='request_authorizer', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, help_text='who accepted (or rejected) this request?', null=True),
        ),
        migrations.AddField(
            model_name='request',
            name='requester',
            field=models.ForeignKey(related_name='requester', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='inbox',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='header',
            name='data',
            field=models.ForeignKey(to='inboxen.HeaderData', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='header',
            name='name',
            field=models.ForeignKey(to='inboxen.HeaderName', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='header',
            name='part',
            field=models.ForeignKey(to='inboxen.PartList'),
        ),
        migrations.AddField(
            model_name='email',
            name='inbox',
            field=models.ForeignKey(to='inboxen.Inbox'),
        ),
        migrations.AddField(
            model_name='domain',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='inbox',
            unique_together=set([('inbox', 'domain')]),
        ),
    ]
