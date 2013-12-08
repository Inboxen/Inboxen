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

import markdown

from django.contrib.auth.models import User
from django.db import models

from inboxen.managers import BodyManager, HeaderManager

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

##
# Inbox models
##

class Domain(models.Model):
    # these are the domains available to create inboxes from
    domain = models.CharField(max_length=253, unique=True)

    def __unicode__(self):
        return self.domain

class Inbox(models.Model):
    inbox = models.CharField(max_length=64)
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField('Created')
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        deleted = ""
        if self.deleted:
            deleted = " (deleted)"
        return u"%s@%s%s" % (self.inbox, self.domain.domain, deleted)

    class Meta:
        verbose_name_plural = "Inboxes"
        unique_together = (('inbox', 'domain'),)

class Tag(models.Model):
    inbox = models.ForeignKey(Inbox)
    tag = models.CharField(max_length=256)

    def __unicode__(self):
        return self.tag

class Request(models.Model):
    amount = models.IntegerField()
    succeeded = models.NullBooleanField(default=None)
    date = models.DateTimeField('requested')
    authorizer = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    requester = models.ForeignKey(User, related_name="requester")
    result = models.CharField(max_length=1024, blank=True, null=True)

##
# Email models
##

class Body(models.Model):
    path = models.FilePathField(default=None, null=True, blank=True)
    hashed = models.CharFields(max_length=80, unique=True) # <algo>:<hash>
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

class PartList(models.Model):
    email = models.ForeignKey(Email)
    body = models.ForeignKey(Body, on_delete=models.PROTECT)
    ordinal = models.IntegerField()

class HeaderName(models.Model):
    # if you're header name is longer than 78, fuck you.
    name = models.CharField(max_length=78, unique=True)

class HeaderData(models.Model):
    hashed = models.CharFields(max_length=80, unique=True) # <algo>:<hash>
    data = models.TextField()

class Header(models.Model):
    name = models.ForeignKey(HeaderName, on_delete=models.PROTECT)
    data = models.ForeignKey(HeaderData, on_delete=models.PROTECT)
    part = models.ForeignKey(PartList)
    ordinal = models.IntegerField()

    objects = HeaderManager()

    def __unicode__():
        return u"{0}".format(self.name.name)

class Email(models.Model):
    inbox = models.ForeignKey(Inbox)
    flags = PositiveSmallIntegerField(default=0) # maybe a custom field + manager that can convert to flag names? :D
    received_date = DateTimeField()

    def get_data(self):
        return hex(self.id)[2:].rstrip("L") # the [2:] is to strip 0x from the start
    
    def set_data(self, data):
        pass # should not be used

    eid = property(get_data, set_data)
