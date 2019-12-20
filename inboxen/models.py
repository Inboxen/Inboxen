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
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils.encoding import smart_str
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from mptt.models import MPTTModel, TreeForeignKey

from inboxen import validators
from inboxen.managers import BodyQuerySet, DomainQuerySet, EmailQuerySet, HeaderQuerySet, InboxQuerySet
from inboxen.search.models import SearchableAbstract
from inboxen.utils.email import unicode_damnit

HEADER_PARAMS = re.compile(r'([a-zA-Z0-9]+)=["\']?([^"\';=]+)["\']?[;]?')


class UserProfile(models.Model):
    """User profile

    Auto-created when accessed via a RelatedManager
    """
    # display image options
    ASK = 0
    DISPLAY = 1
    NO_DISPLAY = 2
    IMAGE_OPTIONS = (
        (ASK, _("Always ask to display images")),
        (DISPLAY, _("Always display images")),
        (NO_DISPLAY, _("Never display images")),
    )

    # what to do when the user hits their quota (if a quota exists)
    REJECT_MAIL = 0
    DELETE_MAIL = 1
    QUOTA_OPTIONS = (
        (REJECT_MAIL, _("Reject new emails")),
        (DELETE_MAIL, _("Delete old emails")),
    )

    user = AutoOneToOneField(settings.AUTH_USER_MODEL, primary_key=True, related_name="inboxenprofile",
                             on_delete=models.CASCADE)
    prefered_domain = models.ForeignKey("inboxen.Domain", null=True, blank=True, on_delete=models.CASCADE,
                                        help_text=_("Prefer a particular domain when adding a new Inbox"))
    prefer_html_email = models.BooleanField(default=True, verbose_name=_("Prefer HTML emails"))
    unified_has_new_messages = models.BooleanField(default=False)
    auto_delete = models.BooleanField(
        default=False,
        verbose_name=_("Auto-delete emails"),
        help_text=_("Delete emails after %(days)s days. Emails that have been marked as important will not be deleted."
                    ) % {"days": settings.INBOX_AUTO_DELETE_TIME},
    )
    display_images = models.PositiveSmallIntegerField(
        choices=IMAGE_OPTIONS, default=ASK,
        verbose_name=_("Display options for HTML emails"),
        help_text=_("Warning: Images in HTML emails can be used to track if you read an email!"),
    )

    quota_options = models.PositiveSmallIntegerField(
        choices=QUOTA_OPTIONS, default=REJECT_MAIL,
        verbose_name=_("What happens once your email quota is reached?"),
    )
    quota_percent_usage = models.PositiveSmallIntegerField(default=0)
    receiving_emails = models.BooleanField(default=True)

    def get_bools_for_labels(self):
        yield ("new", self.unified_has_new_messages)

    def __str__(self):
        return u"Profile for %s" % self.user


class Statistic(models.Model):
    """Statistics about users"""
    date = models.DateTimeField('date', auto_now_add=True, db_index=True)

    users = JSONField()
    emails = JSONField()
    inboxes = JSONField()

    def __str__(self):
        return str(self.date)


class Liberation(models.Model):
    """Liberation data

    `async_result` is the UUID of Celery result object, which may or may not be valid
    `_path` is relative to settings.SENDFILE_ROOT
    """
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    content_type = models.PositiveSmallIntegerField(default=0)
    async_result = models.UUIDField(null=True)
    started = models.DateTimeField(null=True)
    last_finished = models.DateTimeField(null=True)
    _path = models.CharField(max_length=255, null=True, unique=True,
                             validators=[validators.ProhibitNullCharactersValidator()])

    running = models.BooleanField(default=False)
    errored = models.BooleanField(default=False)

    def get_path(self):
        if self._path is None:
            return None
        return os.path.join(settings.SENDFILE_ROOT, self._path)

    def set_path(self, path):
        assert path[0] != "/", "path should be relative, not absolute"
        self._path = os.path.join(settings.SENDFILE_ROOT, path)

    path = property(get_path, set_path)

    def __str__(self):
        return u"Liberation for %s" % self.user


##
# Inbox models
##


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


class Inbox(SearchableAbstract):
    """Inbox model

    Object manager has a custom create() method to generate a random local part
    and a from_string() method to grab an Inbox object from the database given
    a string "inbox@domain"
    """
    inbox = models.CharField(max_length=64, validators=[validators.ProhibitNullCharactersValidator()])
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField('Created')
    description = models.CharField(max_length=256, null=True, blank=True,
                                   validators=[validators.ProhibitNullCharactersValidator()])

    deleted = models.BooleanField(default=False)
    new = models.BooleanField(default=False)
    exclude_from_unified = models.BooleanField(default=False, verbose_name=_("Exclude from Unified Inbox"))
    disabled = models.BooleanField(default=False, verbose_name=_("Disable Inbox"),
                                   help_text=_("This Inbox will no longer receive emails."))
    pinned = models.BooleanField(default=False, verbose_name=_("Pin Inbox to top"))

    objects = InboxQuerySet.as_manager()

    _bool_label_order = ["new", "disabled", "pinned"]

    def get_bools_for_labels(self):
        for key in self._bool_label_order:
            yield (key, getattr(self, key))

    def __str__(self):
        return u"%s@%s" % (self.inbox, self.domain.domain)

    def __repr__(self):
        u_rep = str(self)
        if self.deleted:
            u_rep = "%s (deleted)" % u_rep
        return smart_str(u'<%s: %s>' % (self.__class__.__name__, u_rep), errors="replace")

    def index_search_a(self):
        return self.description or ""

    def index_search_b(self):
        return str(self)

    class Meta:
        verbose_name_plural = "Inboxes"
        unique_together = (('inbox', 'domain'),)
        indexes = [GinIndex(fields=["search_tsv"])]

##
# Email models
##


class Email(SearchableAbstract):
    """Email model

    eid is a convience property that outputs a hexidec ID

    The body and headers can be found in the root of the PartList tree on Email.parts
    """
    inbox = models.ForeignKey(Inbox, on_delete=models.CASCADE)
    received_date = models.DateTimeField(db_index=True)

    deleted = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    seen = models.BooleanField(default=False)
    important = models.BooleanField(default=False)
    view_all_headers = models.BooleanField(default=False)

    objects = EmailQuerySet.as_manager()

    @property
    def eid(self):
        """Return a hexidecimal version of ID"""
        return hex(self.id)[2:].rstrip("L")

    _bool_label_order = ["read", "seen", "important"]

    def get_bools_for_labels(self):
        for key in self._bool_label_order:
            yield (key, getattr(self, key))

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

    def index_search_a(self):
        try:
            subject = HeaderData.objects.filter(
                header__part__parent__isnull=True,
                header__name__name="Subject",
                header__part__email__id=self.id,
            ).first()

            return unicode_damnit(subject.data)
        except AttributeError:
            return ""

    def index_search_b(self):
        try:
            from_header = HeaderData.objects.filter(
                header__part__parent__isnull=True,
                header__name__name="From",
                header__part__email__id=self.id,
            ).first()

            return unicode_damnit(from_header.data)
        except AttributeError:
            return ""

    class Meta:
        indexes = [GinIndex(fields=["search_tsv"])]


class Body(models.Model):
    """Body model

    Object manager has a get_or_create() method that deals with duplicated
    bodies.

    This model expects and returns binary data, converting to and from str happens elsewhere
    """
    hashed = models.CharField(max_length=80, unique=True,
                              validators=[validators.ProhibitNullCharactersValidator()])  # <algo>:<hash>
    data = models.BinaryField(default=b"")

    objects = BodyQuerySet.as_manager()

    def __str__(self):
        return self.hashed


class PartList(MPTTModel):
    """Part model

    non-MIME part or MIME part(s)

    See MPTT docs on how to use this model

    email is passed to Email as a workaround for https://github.com/django-mptt/django-mptt/issues/189
    """
    email = models.ForeignKey(Email, related_name='parts', on_delete=models.CASCADE)
    body = models.ForeignKey(Body, on_delete=models.PROTECT)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

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


class HeaderName(models.Model):
    """Header name model

    Limited to 78 characters
    """
    name = models.CharField(max_length=78, unique=True, validators=[validators.ProhibitNullCharactersValidator()])

    def __str__(self):
        return self.name


class HeaderData(models.Model):
    """Header data model

    RFC 2822 implies that header data may be infinite, may as well support it!
    """
    hashed = models.CharField(max_length=80, unique=True,
                              validators=[validators.ProhibitNullCharactersValidator()])  # <algo>:<hash>
    data = models.TextField(validators=[validators.ProhibitNullCharactersValidator()])

    def __str__(self):
        return self.hashed


class Header(models.Model):
    """Header model

    ordinal preserves the order of headers as in the original message

    Object manager has a create() method that accepts name and data, it deals
    with duplicated header names/data behind the scenes
    """
    name = models.ForeignKey(HeaderName, on_delete=models.PROTECT)
    data = models.ForeignKey(HeaderData, on_delete=models.PROTECT)
    part = models.ForeignKey(PartList, on_delete=models.CASCADE)
    ordinal = models.IntegerField()

    objects = HeaderQuerySet.as_manager()

    def __str__(self):
        return u"{0}".format(self.name.name)
