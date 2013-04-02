from django.db import models
from django.contrib.auth.models import User

class Alias(models.Model):
	alias = models.CharField(max_length=1024)
	user = models.ForeignKey(User) 

class Attachment(models.Model):
	pass

class Header(models.Model):
	name = models.CharField(max_length=1024)
	data = models.CharField(max_length=1024)	

class Email(models.Model):
	headers = models.ManyToManyField(Header)
	user = models.ForeignKey(User, related_name='user')
	inbox = models.ForeignKey(Alias)
	body = models.TextField()
	attachments = models.ManyToManyField(Attachment)
	recieved_date = models.DateTimeField('Recieved Date')
