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

from annoying.fields import AutoOneToOneField, JSONField
from bitfield import BitField
from django.conf import settings
from django.db import models, transaction
from django.utils.encoding import smart_str
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
import six

from inboxen.managers import BodyQuerySet, DomainQuerySet, EmailQuerySet, HeaderQuerySet, InboxQuerySet
from inboxen import validators

HEADER_PARAMS = re.compile(r'([a-zA-Z0-9]+)=["\']?([^"\';=]+)["\']?[;]?')


@six.python_2_unicode_compatible
class UserProfile(models.Model):
    """This is auto-created when accessed via a RelatedManager

    Flag definitions are as follows, order !!important!!:
    prefer_html_email - if we have both HTML and plaintext available, prefer
                        HTML if set, prefer plain if not
    unified_has_new_messages - controls the display of the `new` badge on the Unified inbox
    ask_images - should we offer to enable image display for HTML emails?
    display_images - should we display images in HTML emails by default? Implies we should never ask
    """
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, primary_key=True, related_name="inboxenprofile")
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

    def __str__(self):
        return u"Profile for %s" % self.user


@six.python_2_unicode_compatible
class Statistic(models.Model):
    """Statistics about users"""
    date = models.DateTimeField('date', auto_now_add=True, db_index=True)

    users = JSONField()
    emails = JSONField()
    inboxes = JSONField()

    def __str__(self):
        return six.text_type(self.date)


@six.python_2_unicode_compatible
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
    _path = models.CharField(max_length=255, null=True, unique=True, validators=[validators.ProhibitNullCharactersValidator()])

    def get_path(self):
        if self._path is None:
            return None
        return os.path.join(settings.LIBERATION_PATH, self._path)

    def set_path(self, path):
        assert path[0] != "/", "path should be relative, not absolute"
        self._path = os.path.join(settings.LIBERATION_PATH, path)

    path = property(get_path, set_path)

    def __str__(self):
        return u"Liberation for %s" % self.user


##
# Inbox models
##


@six.python_2_unicode_compatible
class Domain(models.Model):
    """Domain model

    `owner` is the user who controls the domain
    """
    domain = models.CharField(max_length=253, unique=True, validators=[validators.ProhibitNullCharactersValidator()])
    enabled = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, default=None, on_delete=models.PROTECT)

    objects = DomainQuerySet.as_manager()

    def __str__(self):
        return self.domain


@six.python_2_unicode_compatible
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
    inbox = models.CharField(max_length=64, validators=[validators.ProhibitNullCharactersValidator()])
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField('Created')
    flags = BitField(flags=("deleted", "new", "exclude_from_unified", "disabled", "pinned"), default=0)
    description = models.CharField(max_length=256, null=True, blank=True, validators=[validators.ProhibitNullCharactersValidator()])

    objects = InboxQuerySet.as_manager()

    def __str__(self):
        return u"%s@%s" % (self.inbox, self.domain.domain)

    def __repr__(self):
        u_rep = six.text_type(self)
        if self.flags.deleted:
            u_rep = "%s (deleted)" % u_rep
        return smart_str(u'<%s: %s>' % (self.__class__.__name__, u_rep), errors="replace")

    class Meta:
        verbose_name_plural = "Inboxes"
        unique_together = (('inbox', 'domain'),)


@six.python_2_unicode_compatible
class Request(models.Model):
    """Inbox allocation request model"""
    amount = models.IntegerField(help_text=_("Pool increase requested"))
    succeeded = models.NullBooleanField("accepted", default=None, help_text=_("has the request been accepted?"))
    date = models.DateTimeField("requested", auto_now_add=True, db_index=True, help_text=_("date requested"))
    date_decided = models.DateTimeField(null=True, help_text=_("date staff accepted/rejected request"))
    authorizer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="request_authorizer",
        blank=True, null=True, on_delete=models.SET_NULL, help_text=_("who accepted (or rejected) this request?"))
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="requester")
    result = models.CharField("comment", max_length=1024, blank=True, null=True, validators=[validators.ProhibitNullCharactersValidator()])

    def save(self, *args, **kwargs):
        if self.succeeded:
            self.requester.inboxenprofile.pool_amount = models.F("pool_amount") + self.amount
            self.requester.inboxenprofile.save(update_fields=["pool_amount"])
        super(Request, self).save(*args, **kwargs)

    def __str__(self):
        return u"Request for %s (%s)" % (self.requester, self.succeeded)

##
# Email models
##


@six.python_2_unicode_compatible
class Email(models.Model):
    """Email model

    eid is a convience property that outputs a hexidec ID
    flags is a BitField for flags such as deleted, read, etc.

    The body and headers can be found in the root of the PartList tree on Email.parts
    """
    inbox = models.ForeignKey(Inbox)
    flags = BitField(flags=("deleted", "read", "seen", "important", "view_all_headers"), default=0)
    received_date = models.DateTimeField(db_index=True)

    objects = EmailQuerySet.as_manager()

    @property
    def eid(self):
        """Return a hexidecimal version of ID"""
        return hex(self.id)[2:].rstrip("L")

    def __str__(self):
        return u"{0}".format(self.eid)

    def get_parts(self):
        """Fetches the MIME tree of the email and returns the root part.

        All subsequent calls to `part.parent` or `part.get_children()` will not
        cause additional database queries
        """
        root_parts = self.parts.all().get_cached_trees()

        assert len(root_parts) <= 1, "Expected to find a single part, found %s" % len(root_parts)

        try:
            return root_parts[0]
        except IndexError:
            return None


@six.python_2_unicode_compatible
class Body(models.Model):
    """Body model

    Object manager has a get_or_create() method that deals with duplicated
    bodies.

    This model expects and returns binary data, converting to and from six.text_type happens elsewhere
    """
    hashed = models.CharField(max_length=80, unique=True, validators=[validators.ProhibitNullCharactersValidator()])  # <algo>:<hash>
    data = models.BinaryField(default="")
    size = models.PositiveIntegerField(null=True)

    objects = BodyQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if self.size is None:
            self.size = len(self.data)
        return super(Body, self).save(*args, **kwargs)

    def __str__(self):
        return self.hashed


@six.python_2_unicode_compatible
class PartList(MPTTModel):
    """Part model

    non-MIME part or MIME part(s)

    See MPTT docs on how to use this model

    email is passed to Email as a workaround for https://github.com/django-mptt/django-mptt/issues/189
    """
    email = models.ForeignKey(Email, related_name='parts')
    body = models.ForeignKey(Body, on_delete=models.PROTECT)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    def __str__(self):
        return six.text_type(self.id)

    @cached_property
    def _content_headers_cache(self):
        """Fetch Content-Type and Content-Disposition headers and split them
        out into useful bits, e.g. filename, charset, etc.

        Properties content_type, filename, and charset use this cached property.
        """
        data = {}
        part_headers = self.header_set.get_many("Content-Type", "Content-Disposition")

        # split off the parameters from the actual content type
        content_header = part_headers.pop("Content-Type", u"").split(";", 1)
        data['content_type'] = content_header[0]
        content_params = content_header[1] if len(content_header) > 1 else u""

        if not self.is_leaf_node():
            # only leaf nodes will have things like charsets and filenames
            return data

        dispos = part_headers.pop("Content-Disposition", u"")

        params = dict(HEADER_PARAMS.findall(content_params))
        params.update(dict(HEADER_PARAMS.findall(dispos)))

        # find filename, could be anywhere, could be nothing
        data["filename"] = params.get("filename") or params.get("name") or u""

        # grab charset
        data["charset"] = params.get("charset", u"utf-8")

        return data

    @property
    def content_type(self):
        return self._content_headers_cache.get("content_type")

    @property
    def filename(self):
        return self._content_headers_cache.get("filename")

    @property
    def charset(self):
        return self._content_headers_cache.get("charset")


@six.python_2_unicode_compatible
class HeaderName(models.Model):
    """Header name model

    Limited to 78 characters
    """
    name = models.CharField(max_length=78, unique=True, validators=[validators.ProhibitNullCharactersValidator()])

    def __str__(self):
        return self.name


@six.python_2_unicode_compatible
class HeaderData(models.Model):
    """Header data model

    RFC 2822 implies that header data may be infinite, may as well support it!
    """
    hashed = models.CharField(max_length=80, unique=True, validators=[validators.ProhibitNullCharactersValidator()])  # <algo>:<hash>
    data = models.TextField(validators=[validators.ProhibitNullCharactersValidator()])

    def __str__(self):
        return self.hashed


@six.python_2_unicode_compatible
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

    def __str__(self):
        return u"{0}".format(self.name.name)
