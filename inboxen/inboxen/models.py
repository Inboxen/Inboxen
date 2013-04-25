import base64

from django.db import models
from django.contrib.auth.models import User

class Domain(models.Model):
    # these are the domains available to create aliases from
    domain = models.CharField(max_length=256)

    def __unicode__(self):
        return self.domain

class Alias(models.Model):
    alias = models.CharField(max_length=512)
    domain = models.ForeignKey(Domain)
    user = models.ForeignKey(User) 
    created = models.DateTimeField('Created')

    def __unicode__(self):
        return u"%s@%s" % (self.alias, self.domain.domain)

class Attachment(models.Model):
    content_type = models.CharField(max_length=256, null=True, blank=True)
    content_disposition = models.CharField(max_length=512, null=True, blank=True)

    _data = models.TextField(
        db_column='data',
        blank=True)

    def set_data(self, data):
        try:
            data = data.encode("utf-8")
        except UnicodeError:
            data = u''

        self._data = base64.encodestring(data)

    def get_data(self):
        return base64.decodestring(self._data)

    data = property(get_data, set_data)

class Tag(models.Model):
    alias = models.ForeignKey(Alias)
    tag = models.CharField(max_length=256)

    def __unicode__(self):
        return self.tag

class Header(models.Model):
    name = models.CharField(max_length=1024)
    data = models.CharField(max_length=1024)    

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    html_preference = models.IntegerField(default=2) # prefer-HTML emails by default

class Email(models.Model):
    read = models.BooleanField(default=False)
    headers = models.ManyToManyField(Header)
    user = models.ForeignKey(User, related_name='user')
    inbox = models.ForeignKey(Alias)
    body = models.TextField(null=True)
    attachments = models.ManyToManyField(Attachment)
    recieved_date = models.DateTimeField('Recieved Date')

