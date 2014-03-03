# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BlogPost'
        db.create_table(u'inboxen_blogpost', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('modified', self.gf('django.db.models.fields.DateTimeField')()),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('draft', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'inboxen', ['BlogPost'])

        # Adding model 'Domain'
        db.create_table(u'inboxen_domain', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=253)),
        ))
        db.send_create_signal(u'inboxen', ['Domain'])

        # Adding model 'Inbox'
        db.create_table(u'inboxen_inbox', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inbox', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inboxen.Domain'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'inboxen', ['Inbox'])

        # Adding model 'Request'
        db.create_table(u'inboxen_request', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('succeeded', self.gf('django.db.models.fields.NullBooleanField')(default=None, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('authorizer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('requester', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requester', to=orm['auth.User'])),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
        ))
        db.send_create_signal(u'inboxen', ['Request'])

        # Adding model 'Attachment'
        db.create_table(u'inboxen_attachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('content_disposition', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('path', self.gf('django.db.models.fields.FilePathField')(default=None, max_length=100, null=True, blank=True)),
            ('_data', self.gf('django.db.models.fields.TextField')(null=True, db_column='data', blank=True)),
        ))
        db.send_create_signal(u'inboxen', ['Attachment'])

        # Adding model 'Tag'
        db.create_table(u'inboxen_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inbox', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inboxen.Inbox'])),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'inboxen', ['Tag'])

        # Adding model 'Header'
        db.create_table(u'inboxen_header', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal(u'inboxen', ['Header'])

        # Adding model 'Email'
        db.create_table(u'inboxen_email', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('read', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user', to=orm['auth.User'])),
            ('inbox', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inboxen.Inbox'])),
            ('body', self.gf('django.db.models.fields.TextField')(null=True)),
            ('recieved_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'inboxen', ['Email'])

        # Adding M2M table for field headers on 'Email'
        m2m_table_name = db.shorten_name(u'inboxen_email_headers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('email', models.ForeignKey(orm[u'inboxen.email'], null=False)),
            ('header', models.ForeignKey(orm[u'inboxen.header'], null=False))
        ))
        db.create_unique(m2m_table_name, ['email_id', 'header_id'])

        # Adding M2M table for field attachments on 'Email'
        m2m_table_name = db.shorten_name(u'inboxen_email_attachments')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('email', models.ForeignKey(orm[u'inboxen.email'], null=False)),
            ('attachment', models.ForeignKey(orm[u'inboxen.attachment'], null=False))
        ))
        db.create_unique(m2m_table_name, ['email_id', 'attachment_id'])

        # Adding model 'UserProfile'
        db.create_table(u'inboxen_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('html_preference', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('pool_amount', self.gf('django.db.models.fields.IntegerField')(default=500)),
        ))
        db.send_create_signal(u'inboxen', ['UserProfile'])

        # Adding model 'TOTPAuth'
        db.create_table(u'inboxen_totpauth', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'inboxen', ['TOTPAuth'])

        # Adding model 'Statistic'
        db.create_table(u'inboxen_statistic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_count', self.gf('django.db.models.fields.IntegerField')()),
            ('active_count', self.gf('django.db.models.fields.IntegerField')()),
            ('new_count', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'inboxen', ['Statistic'])


    def backwards(self, orm):
        # Deleting model 'BlogPost'
        db.delete_table(u'inboxen_blogpost')

        # Deleting model 'Domain'
        db.delete_table(u'inboxen_domain')

        # Deleting model 'Inbox'
        db.delete_table(u'inboxen_inbox')

        # Deleting model 'Request'
        db.delete_table(u'inboxen_request')

        # Deleting model 'Attachment'
        db.delete_table(u'inboxen_attachment')

        # Deleting model 'Tag'
        db.delete_table(u'inboxen_tag')

        # Deleting model 'Header'
        db.delete_table(u'inboxen_header')

        # Deleting model 'Email'
        db.delete_table(u'inboxen_email')

        # Removing M2M table for field headers on 'Email'
        db.delete_table(db.shorten_name(u'inboxen_email_headers'))

        # Removing M2M table for field attachments on 'Email'
        db.delete_table(db.shorten_name(u'inboxen_email_attachments'))

        # Deleting model 'UserProfile'
        db.delete_table(u'inboxen_userprofile')

        # Deleting model 'TOTPAuth'
        db.delete_table(u'inboxen_totpauth')

        # Deleting model 'Statistic'
        db.delete_table(u'inboxen_statistic')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'inboxen.attachment': {
            'Meta': {'object_name': 'Attachment'},
            '_data': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'data'", 'blank': 'True'}),
            'content_disposition': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.FilePathField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'inboxen.blogpost': {
            'Meta': {'object_name': 'BlogPost'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'draft': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'inboxen.domain': {
            'Meta': {'object_name': 'Domain'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '253'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'inboxen.email': {
            'Meta': {'object_name': 'Email'},
            'attachments': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['inboxen.Attachment']", 'symmetrical': 'False'}),
            'body': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'headers': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['inboxen.Header']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inbox': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.Inbox']"}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'recieved_date': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': u"orm['auth.User']"})
        },
        u'inboxen.header': {
            'Meta': {'object_name': 'Header'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        u'inboxen.inbox': {
            'Meta': {'object_name': 'Inbox'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.Domain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inbox': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'inboxen.request': {
            'Meta': {'object_name': 'Request'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'authorizer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requester'", 'to': u"orm['auth.User']"}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'succeeded': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        u'inboxen.statistic': {
            'Meta': {'object_name': 'Statistic'},
            'active_count': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_count': ('django.db.models.fields.IntegerField', [], {}),
            'user_count': ('django.db.models.fields.IntegerField', [], {})
        },
        u'inboxen.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inbox': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.Inbox']"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'inboxen.totpauth': {
            'Meta': {'object_name': 'TOTPAuth'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'inboxen.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'html_preference': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pool_amount': ('django.db.models.fields.IntegerField', [], {'default': '500'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['inboxen']