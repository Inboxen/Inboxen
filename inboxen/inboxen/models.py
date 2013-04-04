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
    pass

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
    spam_filtering = models.BooleanField()
    premium = models.BooleanField()  

class Email(models.Model):
    headers = models.ManyToManyField(Header)
    user = models.ForeignKey(User, related_name='user')
    inbox = models.ForeignKey(Alias)
    body = models.TextField()
    attachments = models.ManyToManyField(Attachment)
    recieved_date = models.DateTimeField('Recieved Date')

