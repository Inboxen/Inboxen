##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
#   
#    This file is part of Inboxen front-end.
#
#    Inboxen front-end is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen front-end is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen front-end.  If not, see <http://www.gnu.org/licenses/>.
##

import base64

from celery import group
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.db import models
from django.dispatch import receiver


class BlogPost(models.Model):
    subject = models.CharField(max_length=512)
    body = models.TextField()
    date = models.DateTimeField('posted')
    modified = models.DateTimeField('modified')
    author = models.ForeignKey(User)
    draft = models.BooleanField(default=True)

class Domain(models.Model):
    # these are the domains available to create inboxes from
    domain = models.CharField(max_length=253)

    def __unicode__(self):
        return self.domain

class Inbox(models.Model):
    inbox = models.CharField(max_length=64)
    domain = models.ForeignKey(Domain, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created = models.DateTimeField('Created')
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        deleted = ""
        if self.deleted:
            deleted = " (deleted)"
        return u"%s@%s%s" % (self.inbox, self.domain.domain, deleted)

    class Meta:
        verbose_name_plural = "Inboxes"
        #unique_together = (('inbox', 'domain'),)

class Request(models.Model):
    amount = models.IntegerField()
    succeeded = models.NullBooleanField(default=None)
    date = models.DateTimeField('requested')
    authorizer = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    requester = models.ForeignKey(User, related_name="requester")
    result = models.CharField(max_length=1024, blank=True, null=True)


class Attachment(models.Model):
    children = models.ManyToManyField(Attachment, symmetrical=False)
    content_type = models.CharField(max_length=256, null=True, blank=True)
    content_disposition = models.CharField(max_length=512, null=True, blank=True)

    path = models.FilePathField(default=None, null=True, blank=True)
    _data = models.TextField(
        db_column='data',
        blank=True,
        null=True,
    )

    def set_data(self, data):
        try:
            data = data.encode("utf-8")
        except UnicodeError:
            data = u''

        self._data = base64.encodestring(data)

    def get_data(self):
        if not self.path:
            return base64.decodestring(self._data)
        
        # look for data in the path
        _tpath = open(self.path, "rb")
        try:
            d = _tpath.read()
        except:
            # be good now.
            _tpath.close()
            raise
        _tpath.close()
        return d
        

    data = property(get_data, set_data)

    def __unicode__(self):
        return self.data

class Tag(models.Model):
    inbox = models.ForeignKey(Inbox)
    tag = models.CharField(max_length=256)

    def __unicode__(self):
        return self.tag

class Header(models.Model):
    name = models.CharField(max_length=1024)
    data = models.CharField(max_length=1024)    

class Email(models.Model):
    read = models.BooleanField(default=False)
    headers = models.ManyToManyField(Header)
    user = models.ForeignKey(User, related_name='user')
    inbox = models.ForeignKey(Inbox)
    body = models.TextField(null=True)
    attachments = models.ManyToManyField(Attachment)
    recieved_date = models.DateTimeField('Recieved Date')
    deleted = models.BooleanField(default=False)

    def get_data(self):
        return hex(self.id)[2:].rstrip("L") # the [2:] is to strip 0x from the start
    
    def set_data(self, data):
        pass # should not be used

    eid = property(get_data, set_data)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    html_preference = models.IntegerField(default=2) # prefer-HTML emails by default
    pool_amount = models.IntegerField(default=500)

class TOTPAuth(models.Model):
    user = models.OneToOneField(User)
    # base32 encoded and do you really want to type 128 characters into your phone?
    # (might raise this later, need to test how bad this is perf. wise)
    secret = models.CharField(max_length=128)

class Statistic(models.Model):
    # statistics about users
    user_count = models.IntegerField()
    active_count = models.IntegerField()

    # generic
    new_count = models.IntegerField()
    date = models.DateTimeField('date')

@receiver(pre_delete, dispatch_uid="I'm unique :3")
def cascade_delete(sender, instance, **kwargs):
    """Fake cascading deletes over ManyToMany relationships for the Email model"""
    if not (sender == Email or sender._meta.proxy_for_model == Email):
        return
    # import here, we need the models to be initialised first :P
    from queue.delete.tasks import delete_email_item

    # delete attachments
    attachments = group([delete_email_item.s('attachment', attachment.id) for attachment in instance.attachments.only('id')])

    # delete headers
    headers = group([delete_email_item.s('header', header.id) for header in instance.headers.only('id')])

    # sometimes an email will have no headers or attachments
    try:
        headers.apply_async()
    except IndexError:
        pass
    try:
        attachments.apply_async()
    except IndexError:
        pass
