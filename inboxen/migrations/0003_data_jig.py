# -*- coding: utf-8 -*-
from south.v2 import DataMigration

import hashlib
import mptt
from django.utils.encoding import smart_bytes

class Migration(DataMigration):
    COLUMN_HASHER = 'sha1'
    FLAGS = {"deleted":1, "read":2, "seen":4}

    def hash_it(self, data):
        hashed = hashlib.new(self.COLUMN_HASHER)
        hashed.update(smart_bytes(data))
        hashed = "{0}:{1}".format(hashed.name, hashed.hexdigest())

        return hashed

    def make_body(self, orm, data=None, path=None):
        if path is None:
            hashed = self.hash_it(data)
        else:
            try:
                file = open(path, "r")
                file_data = file.read()
            finally:
                file.close()
            hashed = self.hash_it(file_data)

        body = orm.Body.objects.get_or_create(hashed=hashed, defaults={'path':path, '_data':data})

        return body[0]

    def make_header(self, orm, name, data, part, ordinal):
        name = orm.HeaderName.objects.get_or_create(name=name)
        data = orm.HeaderData.objects.get_or_create(hashed=self.hash_it(data), defaults={"data": data})
        orm.NewHeader.objects.create(name=name, data=data, part=part, ordinal=ordinal)

    def flag_setter(self, email):
        flags = 0
        if email.read:
            flags = flags | self.FLAGS["read"]
        elif email.deleted:
            flags = flags | self.FLAGS["deleted"]

        email.update(flags=flags)

    def forwards(self, orm):
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.

        # Take PartList and "extend" it with mtpp stuff
        # http://django-mptt.github.io/django-mptt/models.html#registration-of-existing-models
        mptt.register(orm.PartList)

        with orm.PartList.objects.delay_mptt_updates():
            for email in orm.Email.objects.all():
                self.flag_setter(email)

                try:
                    body = email.body.encode("utf8")
                except UnicodeError:
                    body = email.body

                body = self.make_body(orm, data=body)
                first_part = orm.PartList(body=body, parent=None)
                first_part.save()

                ordinal = 0
                for header in email.headers.all():
                    self.make_header(orm, name=header.name, data=header.data, part=first_part, ordinal=ordinal)
                    ordinal = ordinal + 1

                for attachment in email.attachments.all():
                    body = self.make_body(orm, data=attachment._data, path=attachment.path)
                    part = orm.PartList(body=body, parent=first_part)
                    part.save()

                    self.make_header(orm, name="Content-Type", data=attachment.content_type, part=part, ordinal=0)
                    self.make_header(orm, name="Content-Disposition", data=attachment.content_disposition, part=part, ordinal=1)

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
    symmetrical = True
