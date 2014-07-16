# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Tag'
        db.delete_table(u'inboxen_tag')


    def backwards(self, orm):
        # Adding model 'Tag'
        db.create_table(u'inboxen_tag', (
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=256, db_index=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inbox', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inboxen.Inbox'])),
        ))
        db.send_create_signal(u'inboxen', ['Tag'])


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
            'data': ('django.db.models.fields.BinaryField', [], {'default': "''"}),
            'hashed': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        },
        u'inboxen.domain': {
            'Meta': {'object_name': 'Domain'},
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '253'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'inboxen.email': {
            'Meta': {'object_name': 'Email'},
            'flags': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inbox': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.Inbox']"}),
            'received_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'inboxen.header': {
            'Meta': {'object_name': 'Header'},
            'data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.HeaderData']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.HeaderName']", 'on_delete': 'models.PROTECT'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.PartList']"})
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
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inboxen.Domain']", 'on_delete': 'models.PROTECT'}),
            'flags': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inbox': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        u'inboxen.liberation': {
            'Meta': {'object_name': 'Liberation'},
            'async_result': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True'}),
            'content_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'data': ('djorm_pgbytea.lobject.LargeObjectField', [], {'null': 'True'}),
            'flags': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'last_finished': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'user': ('inboxen.fields.DeferAutoOneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
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
        u'inboxen.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'flags': ('django.db.models.fields.BigIntegerField', [], {'default': '5'}),
            'pool_amount': ('django.db.models.fields.IntegerField', [], {'default': '500'}),
            'user': ('annoying.fields.AutoOneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['inboxen']