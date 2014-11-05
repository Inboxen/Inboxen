##
#    Copyright (C) 2013, 2014 Jessica Tallon & Matt Molyneaux
#
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

from datetime import datetime
import re

from django.conf import settings
from django.db import models, transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

from annoying.fields import AutoOneToOneField, JSONField
from bitfield import BitField
from django_extensions.db.fields import UUIDField
from djorm_pgbytea.fields import LargeObjectField, LargeObjectFile
from model_utils.managers import PassThroughManager
from mptt.models import MPTTModel, TreeForeignKey
from pytz import utc
import watson

from inboxen.managers import BodyQuerySet, HeaderQuerySet, InboxQuerySet
from inboxen import fields, search

HEADER_PARAMS = re.compile(r'([a-zA-Z0-9]+)=["\']?([^"\';=]+)["\']?[;]?')


class UserProfile(models.Model):
    """This is auto-created when accessed via a RelatedManager

    Flag definitions are as follows, order !!important!!:
    prefer_html_email - if we have both HTML and plaintext available, prefer
                        HTML if set, prefer plain if not
    unified_has_new_messages - controls the display of the `new` badge on the Unified inbox
    ask_images - should we offer to enable image display for HTML emails?
    display_images - should we display images in HTML emails by default? Implies we should never ask
    """
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    pool_amount = models.IntegerField(default=500)
    flags = BitField(flags=("prefer_html_email", "unified_has_new_messages", "ask_images", "display_images"), default=5)

    def available_inboxes(self):
        used = self.user.inbox_set.count()
        left = self.pool_amount - used

        if left < settings.MIN_INBOX_FOR_REQUEST:
            with transaction.atomic():
                try:
                    last_request = self.user.requester.order_by('-date').only('succeeded')[0].succeeded
                except IndexError:
                    last_request = True

                if last_request:
                    amount = self.pool_amount + settings.REQUEST_NUMBER
                    Request.objects.create(amount=amount, requester=self.user)

        return left

    def __unicode__(self):
        return self.user.username


class Statistic(models.Model):
    """Statistics about users"""
    date = models.DateTimeField('date')

    users = JSONField()
    emails = JSONField()
    inboxes = JSONField()


class Liberation(models.Model):
    """Liberation data

    `payload` is the compressed archive - it is not base64 encoded
    `async_result` is the UUID of Celery result object, which may or may not be valid
    """
    user = fields.DeferAutoOneToOneField(settings.AUTH_USER_MODEL, primary_key=True, defer_fields=["data"])
    flags = BitField(flags=("running", "errored"), default=0)
    data = LargeObjectField(null=True)
    content_type = models.PositiveSmallIntegerField(default=0)
    async_result = UUIDField(auto=False, null=True)
    started = models.DateTimeField(null=True)
    last_finished = models.DateTimeField(null=True)
    size = models.PositiveIntegerField(null=True)

    def set_payload(self, data):
        if data is None:
            self.data = None
            return
        elif self.data is None:
            self.data = LargeObjectFile(0)

        file = self.data.open(mode="wb")
        file.write(data)
        file.close()

        self.size = len(data)

    def get_payload(self):
        with transaction.atomic():
            if self.data is None:
                return None
            return buffer(self.data.open(mode="rb").read())

    payload = property(get_payload, set_payload)

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

    `flags` are "deleted" and "new".
    * "deleted" is obvious (and should be used instead of deleting the model)
    * "new" should be set when an email is added to the inbox and unset when
      the inbox is viewed
    * "disabled" is a bit like "deleted", but incoming mail will be deffered, not rejected
    """
    inbox = models.CharField(max_length=64)
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField('Created')
    flags = BitField(flags=("deleted", "new", "exclude_from_unified", "disabled"), default=0)
    tags = models.CharField(max_length=256, null=True, blank=True)

    objects = PassThroughManager.for_queryset_class(InboxQuerySet)()

    def __unicode__(self):
        return u"%s@%s" % (self.inbox, self.domain.domain)

    def __repr__(self):
        try:
            u_rep = unicode(self)
        except (UnicodeEncodeError, UnicodeDecodeError):
            u_rep = "[Bad Unicode data]"
        if self.flags.deleted is True:
            u_rep = "%s (deleted)" % u_rep
        return smart_str(u'<%s: %s>' % (self.__class__.__name__, u_rep))

    class Meta:
        verbose_name_plural = "Inboxes"
        unique_together = (('inbox', 'domain'),)


class Request(models.Model):
    """Inbox allocation request model"""
    amount = models.IntegerField(help_text=_("Pool increase requested"))
    succeeded = models.NullBooleanField("accepted", default=None, help_text=_("has the request been accepted?"))
    date = models.DateTimeField("requested", auto_now_add=True, help_text=_("date requested"))
    date_decided = models.DateTimeField(null=True, help_text=_("date staff accepted/rejected request"))
    authorizer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="request_authorizer", blank=True, null=True, on_delete=models.SET_NULL, help_text=_("who accepted (or rejected) this request?"))
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="requester")
    result = models.CharField("comment", max_length=1024, blank=True, null=True)

##
# Email models
##


class Email(models.Model):
    """Email model

    eid is a convience property that outputs a hexidec ID
    flags is a BitField for flags such as deleted, read, etc.

    The body and headers can be found in the root of the PartList tree on Email.parts
    """
    inbox = models.ForeignKey(Inbox)
    flags = BitField(flags=("deleted", "read", "seen", "important", "view_all_headers"), default=0)
    received_date = models.DateTimeField()

    @property
    def eid(self):
        """Return a hexidecimal version of ID"""
        return hex(self.id)[2:].rstrip("L")

    def __unicode__(self):
        return u"{0}".format(self.eid)

    def get_parts(self):
        """Return a list of (<part>, <content headers>)"""
        attachments = []
        for part in self.object.parts.all():
            part_head = part.header_set.get_many("Content-Type", "Content-Disposition")
            part_head["content_type"] = part_head.pop("Content-Type", "").split(";", 1)

            if part_head["content_type"][0].startswith("multipart") or part_head["content_type"][0].startswith("message"):
                continue

            dispos = part_head.pop("Content-Disposition", "")

            try:
                params = dict(HEADER_PARAMS.findall(part_head["content_type"][1]))
            except IndexError:
                params = {}
            params.update(dict(HEADER_PARAMS.findall(dispos)))

            # find filename, could be anywhere
            if "filename" in params:
                part_head["filename"] = params["filename"]
            elif "name" in params:
                part_head["filename"] = params["name"]
            else:
                part_head["filename"] = ""

            # grab charset
            part.charset = params.get("charset", "utf-8")

            attachments.append((part, part_head))

        return attachments


class Body(models.Model):
    """Body model

    Object manager has a get_or_create() method that deals with duplicated
    bodies.

    This model expects and returns binary data, converting to and from unicode happens elsewhere
    """
    hashed = models.CharField(max_length=80, unique=True)  # <algo>:<hash>
    data = models.BinaryField(default="")
    size = models.PositiveIntegerField(null=True)

    objects = PassThroughManager.for_queryset_class(BodyQuerySet)()

    def save(self, *args, **kwargs):
        if self.size is None:
            self.size = len(self.data)
        return super(Body, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.hashed


class PartList(MPTTModel):
    """Part model

    non-MIME part or MIME part(s)

    See MPTT docs on how to use this model

    email is passed to Email as a workaround for https://github.com/django-mptt/django-mptt/issues/189
    """
    email = models.ForeignKey(Email, related_name='parts')
    body = models.ForeignKey(Body, on_delete=models.PROTECT)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    def __unicode__(self):
        return unicode(self.id)


class HeaderName(models.Model):
    """Header name model

    Limited to 78 characters
    """
    name = models.CharField(max_length=78, unique=True)

    def __unicode__(self):
        return self.name


class HeaderData(models.Model):
    """Header data model

    RFC 2822 implies that header data may be infinite, may as well support it!
    """
    hashed = models.CharField(max_length=80, unique=True)  # <algo>:<hash>
    data = models.TextField()

    def __unicode__(self):
        return self.hashed


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

    objects = PassThroughManager.for_queryset_class(HeaderQuerySet)()

    def __unicode__(self):
        return u"{0}".format(self.name.name)

# Unregister update_last_login handler
# See https://github.com/Inboxen/website/issues/156
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import update_last_login

user_logged_in.disconnect(update_last_login)

# Search
watson.register(Email, search.EmailSearchAdapter)
watson.register(Inbox, search.InboxSearchAdapter)

# signals
@receiver(pre_save, sender=Request, dispatch_uid="request_decided_checker")
def decided_checker(sender, instance=None, **kwargs):
    if instance.date_decided is None and instance.succeeded is not None and instance.authorizer is not None:
        instance.date_decided = datetime.now(utc)
        if instance.succeeded is True:
            profile = instance.requester.userprofile
            profile.pool_amount = models.F("pool_amount") + instance.amount
            profile.save(update_fields=["pool_amount"])
    elif instance.authorizer is None or instance.succeeded is None:
        # either authorizer or succeeded is missing, so we'll bug out
        instance.authorizer = None
        instance.succeeded = None
        instance.date_decided = None
