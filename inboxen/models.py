##
#    Copyright (C) 2013, 2014, 2015 Jessica Tallon & Matt Molyneaux
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

import os.path
import re

from django.conf import settings
from django.db import models, transaction
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

from annoying.fields import AutoOneToOneField, JSONField
from bitfield import BitField
from mptt.models import MPTTModel, TreeForeignKey

from inboxen.managers import BodyQuerySet, DomainQuerySet, EmailQuerySet, HeaderQuerySet, InboxQuerySet

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
    prefered_domain = models.ForeignKey("inboxen.Domain", null=True, blank=True)

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
        return unicode(self.user)


class Statistic(models.Model):
    """Statistics about users"""
    date = models.DateTimeField('date')

    users = JSONField()
    emails = JSONField()
    inboxes = JSONField()


class Liberation(models.Model):
    """Liberation data

    `async_result` is the UUID of Celery result object, which may or may not be valid
    `_path` is relative to settings.LIBERATION_PATH
    """
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    flags = BitField(flags=("running", "errored"), default=0)
    content_type = models.PositiveSmallIntegerField(default=0)
    async_result = models.UUIDField(null=True)
    started = models.DateTimeField(null=True)
    last_finished = models.DateTimeField(null=True)
    _path = models.CharField(max_length=255, null=True, unique=True)

    def get_path(self):
        if self._path is None:
            return None
        return os.path.join(settings.LIBERATION_PATH, self._path)

    def set_path(self, path):
        assert path[0] != "/", "path should be relative, not absolute"
        self._path = os.path.join(settings.LIBERATION_PATH, path)

    path = property(get_path, set_path)


##
# Inbox models
##


class Domain(models.Model):
    """Domain model

    `owner` is the user who controls the domain
    """
    domain = models.CharField(max_length=253, unique=True)
    enabled = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, default=None, on_delete=models.PROTECT)

    objects = DomainQuerySet.as_manager()

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
    description = models.CharField(max_length=256, null=True, blank=True)

    objects = InboxQuerySet.as_manager()

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
    authorizer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="request_authorizer",
        blank=True, null=True, on_delete=models.SET_NULL, help_text=_("who accepted (or rejected) this request?"))
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="requester")
    result = models.CharField("comment", max_length=1024, blank=True, null=True)

    def __unicode__(self):
        return u"Request for %s (%s)" % (self.requester, succeeded)

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

    objects = EmailQuerySet.as_manager()

    @property
    def eid(self):
        """Return a hexidecimal version of ID"""
        return hex(self.id)[2:].rstrip("L")

    def __unicode__(self):
        return u"{0}".format(self.eid)

    def get_parts(self):
        """Returns a list of all the MIME parts of this email

        It also annotates objects with useful attributes, such as charset and parent
        (which is a reference to that object in the same queryset rather than a copy as
        Django would do it)
        """
        part_list = list(self.parts.all())
        parents = {}
        for part in part_list:
            part.parent = parents.get(part.parent_id, None)
            part_head = part.header_set.get_many("Content-Type", "Content-Disposition")
            content_header = part_head.pop("Content-Type", "").split(";", 1)
            part.content_type = content_header[0]
            content_params = content_header[1] if len(content_header) > 1 else ""

            part.childs = []

            if part.parent:
                part.parent.childs.append(part)

            if not part.is_leaf_node():
                parents[part.id] = part
                continue

            dispos = part_head.pop("Content-Disposition", "")

            try:
                params = dict(HEADER_PARAMS.findall(content_params))
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

        return part_list


class Body(models.Model):
    """Body model

    Object manager has a get_or_create() method that deals with duplicated
    bodies.

    This model expects and returns binary data, converting to and from unicode happens elsewhere
    """
    hashed = models.CharField(max_length=80, unique=True)  # <algo>:<hash>
    data = models.BinaryField(default="")
    size = models.PositiveIntegerField(null=True)

    objects = BodyQuerySet.as_manager()

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

    objects = HeaderQuerySet.as_manager()

    def __unicode__(self):
        return u"{0}".format(self.name.name)
