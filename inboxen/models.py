##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
#
#    This file is part of Inboxen.
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

from datetime import datetime
import markdown

from django.contrib.auth.models import User
from django.db import models, transaction

from bitfield import BitField
from mptt.models import MPTTModel, TreeForeignKey, TreeOneToOneField
from pytz import utc

from inboxen.managers import BodyManager, HeaderManager, InboxManager

class BlogPost(models.Model):
    subject = models.CharField(max_length=512)
    body = models.TextField()
    date = models.DateTimeField('posted')
    modified = models.DateTimeField('modified')
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    draft = models.BooleanField(default=True)

    @property
    def rendered_body(self):
        return markdown.markdown(self.body)

    def __unicode__(self):
        draft = ""
        if self.draft:
            draft = " (draft)"
        return u"%s%s" % (self.date, draft)

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    html_preference = models.IntegerField(default=2) # prefer-HTML emails by default
    pool_amount = models.IntegerField(default=500)

    def available_inboxes(self):
        used = self.user.inbox_set.count()
        left = self.pool_amount - used

        if left < 10: #TODO: issue #57
            with transaction.atomic():
                try:
                    last_request = self.user.request_set.orderby('-date').only('succeeded')[0].succeeded
                except IndexError:
                    last_request = True

                if last_request:
                    amount = self.pool_amont + 500 #TODO: issue #57
                    request = Request(amount=amount, date=datetime.now(utc))

        return left

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

##
# Inbox models
##

class Domain(models.Model):
    """Domain model"""
    domain = models.CharField(max_length=253, unique=True)

    def __unicode__(self):
        return self.domain

class Inbox(models.Model):
    """Inbox model

    Object manager has a custom create() method to generate a random local part
    and a from_string() method to grab an Inbox object from the database given
    a string "inbox@domain"
    """
    inbox = models.CharField(max_length=64)
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField('Created')
    deleted = models.BooleanField(default=False)

    objects = InboxManager()

    def __unicode__(self):
        deleted = ""
        if self.deleted:
            deleted = " (deleted)"
        return u"%s@%s%s" % (self.inbox, self.domain.domain, deleted)

    class Meta:
        verbose_name_plural = "Inboxes"
        unique_together = (('inbox', 'domain'),)

class Tag(models.Model):
    """Tag model

    Object manager has a from_string() method that returns Tag objects from a
    string.
    """
    tag = models.CharField(max_length=256)
    inbox = models.ForeignKey(Inbox, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.tag

class Request(models.Model):
    """Inbox allocation request model"""
    amount = models.IntegerField()
    succeeded = models.NullBooleanField(default=None)
    date = models.DateTimeField('requested')
    authorizer = models.ForeignKey(User, related_name="request_authorizer", blank=True, null=True, on_delete=models.SET_NULL)
    requester = models.ForeignKey(User, related_name="requester")
    result = models.CharField(max_length=1024, blank=True, null=True)

##
# Email models
##

class Body(models.Model):
    """Body model

    Object manager has a get_or_create() method that deals with duplicated
    bodies.
    """
    path = models.FilePathField(default=None, null=True, blank=True)
    hashed = models.CharField(max_length=80, unique=True) # <algo>:<hash>
    _data = models.BinaryField(
        db_column='data',
        blank=True,
        null=True,
    )

    objects = BodyManager()

    def set_data(self, data):
        try:
            data = data.encode('utf-8')
        except (UnicodeEncodeError, UnicodeEncodeError):
            self._data = data

    def get_data(self):
        if not self.path:
            return self._data
        
        # look for data in the path
        _tpath = open(self.path, "rb")
        try:
            d = _tpath.read()
        finally:
            _tpath.close()
        return d

    data = property(get_data, set_data)

    def __unicode__(self):
        return self.hashed

class PartList(MPTTModel):
    """Part model

    non-MIME part or MIME part(s)

    See MPTT docs on how to use this model

    email is passed to Email as a workaround for https://github.com/django-mptt/django-mptt/issues/189
    """
    body = models.ForeignKey(Body, on_delete=models.PROTECT)
    email = models.PositiveIntegerField()
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    class MPTTMeta:
        tree_id_attr = 'email'

class HeaderName(models.Model):
    """Header name model

    Limited to 78 characters
    """
    name = models.CharField(max_length=78, unique=True)

class HeaderData(models.Model):
    """Header data model

    RFC 2822 implies that header data may be infinite, may as well support it!
    """
    hashed = models.CharField(max_length=80, unique=True) # <algo>:<hash>
    data = models.TextField()

class Header(models.Model):
    """Header model

    ordinal preserves the order of headers as in the original message

    Object manager has a create() method that accepts name and data, it deals
    with duplicated header names/data behind the scenes
    """
    name = models.ForeignKey(HeaderName, on_delete=models.PROTECT)
    data = models.ForeignKey(HeaderData, on_delete=models.PROTECT)
    part = models.ForeignKey(PartList)
    ordinal = models.IntegerField()

    objects = HeaderManager()

    def __unicode__():
        return u"{0}".format(self.name.name)

class Email(models.Model):
    """Email model

    eid is a convience property that outputs a hexidec ID
    flags is a BitField for flags such as deleted, read, etc.

    The body and headers can be found in the root of the PartList tree with
    a tree-id the same as Email.id.
    """
    id = TreeOneToOneField(PartList, primary_key=True, related_name="message")
    inbox = models.ForeignKey(Inbox)
    flags = BitField(flags=("deleted","read","seen"), default=0)
    received_date = models.DateTimeField()

    def get_eid(self):
        return hex(self.id)[2:].rstrip("L") # the [2:] is to strip 0x from the start
    
    def set_eid(self, data):
        pass # should not be used

    eid = property(get_eid, set_eid)
