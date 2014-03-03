# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HeaderData'
        db.create_table(u'inboxen_headerdata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hashed', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'inboxen', ['HeaderData'])

        # Adding model 'Body'
        db.create_table(u'inboxen_body', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.FilePathField')(default=None, max_length=100, null=True, blank=True)),
            ('hashed', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('_data', self.gf('django.db.models.fields.BinaryField')(null=True, db_column='data', blank=True)),
        ))
        db.send_create_signal(u'inboxen', ['Body'])

        # Adding model 'NewHeader'
        db.create_table(u'inboxen_newheader', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inboxen.HeaderName'], on_delete=models.PROTECT)),
            ('data', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inboxen.HeaderData'], on_delete=models.PROTECT)),
            ('part', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inboxen.PartList'])),
            ('ordinal', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'inboxen', ['NewHeader'])

        # Adding model 'PartList'
        db.create_table(u'inboxen_partlist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parts', to=orm['inboxen.Email'])),
            ('body', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inboxen.Body'], on_delete=models.PROTECT)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['inboxen.PartList'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'inboxen', ['PartList'])

        # Adding model 'HeaderName'
        db.create_table(u'inboxen_headername', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=78)),
        ))
        db.send_create_signal(u'inboxen', ['HeaderName'])

        # Adding unique constraint on 'Domain', fields ['domain']
        db.create_unique(u'inboxen_domain', ['domain'])

        # Deleting field 'UserProfile.id'
        db.delete_column(u'inboxen_userprofile', u'id')


        # Changing field 'UserProfile.user'
        db.alter_column(u'inboxen_userprofile', 'user_id', self.gf('annoying.fields.AutoOneToOneField')(to=orm['auth.User'], unique=True, primary_key=True))

        # Rename field 'Email.recieved_date' to 'Email.received_date'
        db.rename_column(u'inboxen_email', 'recieved_date', 'received_date')

        # Deleting field 'Email.user'
        db.delete_column(u'inboxen_email', 'user_id')

        # Adding field 'Email.flags'
        db.add_column(u'inboxen_email', 'flags',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0),
                      keep_default=False)

        # Changing field 'BlogPost.author'
        db.alter_column(u'inboxen_blogpost', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], on_delete=models.PROTECT))

        # Changing field 'TOTPAuth.user'
        db.alter_column(u'inboxen_totpauth', 'user_id', self.gf('annoying.fields.AutoOneToOneField')(to=orm['auth.User'], unique=True))

        # Changing field 'Request.authorizer'
        db.alter_column(u'inboxen_request', 'authorizer_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'Inbox.domain'
        db.alter_column(u'inboxen_inbox', 'domain_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inboxen.Domain'], on_delete=models.PROTECT))

        # Changing field 'Inbox.user'
        db.alter_column(u'inboxen_inbox', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.SET_NULL))
        # Adding unique constraint on 'Inbox', fields ['inbox', 'domain']
        db.create_unique(u'inboxen_inbox', ['inbox', 'domain_id'])


    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration. You backed up, right?")

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
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'on_delete': 'models.PROTECT'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'draft': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'inboxen.body': {
            'Meta': {'object_name': 'Body'},
            '_data': ('django.db.models.fields.BinaryField', [], {'null': 'True', 'db_column': "'data'", 'blank': 'True'}),
            'hashed': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.FilePathField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'inboxen.domain': {
            'Meta': {'object_name': 'Domain'},
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '253'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'inboxen.email': {
            'Meta': {'object_name': 'Email'},
            'attachments': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['inboxen.Attachment']", 'symmetrical': 'False'}),
            'body': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'flags': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'headers': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['inboxen.Header']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inbox': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.Inbox']"}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'received_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'inboxen.header': {
            'Meta': {'object_name': 'Header'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        u'inboxen.headerdata': {
            'Meta': {'object_name': 'HeaderData'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'hashed': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'inboxen.headername': {
            'Meta': {'object_name': 'HeaderName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '78'})
        },
        u'inboxen.inbox': {
            'Meta': {'unique_together': "(('inbox', 'domain'),)", 'object_name': 'Inbox'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.Domain']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inbox': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        u'inboxen.newheader': {
            'Meta': {'object_name': 'NewHeader'},
            'data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.HeaderData']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.HeaderName']", 'on_delete': 'models.PROTECT'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.PartList']"})
        },
        u'inboxen.partlist': {
            'Meta': {'object_name': 'PartList'},
            'body': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.Body']", 'on_delete': 'models.PROTECT'}),
            'email': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parts'", 'to': u"orm['inboxen.Email']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['inboxen.PartList']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'inboxen.request': {
            'Meta': {'object_name': 'Request'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'authorizer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'request_authorizer'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
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
            'user': ('annoying.fields.AutoOneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'inboxen.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'html_preference': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'pool_amount': ('django.db.models.fields.IntegerField', [], {'default': '500'}),
            'user': ('annoying.fields.AutoOneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['inboxen']
