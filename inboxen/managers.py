##
#    Copyright (C) 2013-2014 Jessica Tallon & Matt Molyneaux
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

import hashlib
import random
import string
from datetime import datetime

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from django.conf import settings
from django.db import IntegrityError, models
from django.db.models import F, Q
from django.db.models.sql.aggregates import Max
from django.db.models.query import QuerySet
from django.utils.encoding import smart_bytes
from django.utils.translation import ugettext as _

from pytz import utc

from inboxen.utils import is_reserved


class MaxDefault(Max):
    """A quick hack to get a default value for the Max aggregate

    Based on code from https://code.djangoproject.com/ticket/10929#comment:1
    """
    sql_template = 'COALESCE(%(function)s(%(field)s), %(default)s)'

    def __init__(self, lookup, **extra):
        self.lookup = lookup
        self.extra = extra

    def _default_alias(self):
        return '%s__%s' % (self.lookup, self.__class__.__name__.lower())
    default_alias = property(_default_alias)

    def add_to_query(self, query, alias, col, source, is_summary):
        super(MaxDefault, self).__init__(col, source, is_summary, **self.extra)
        query.aggregate_select[alias] = self


class HashedQuerySet(QuerySet):
    def hash_it(self, data):
        hashed = hashlib.new(settings.COLUMN_HASHER)
        hashed.update(smart_bytes(data))
        hashed = "{0}:{1}".format(hashed.name, hashed.hexdigest())

        return hashed


class DomainQuerySet(QuerySet):
    def available(self, user):
        """Return QuerySet with domains available to user"""
        return self.filter(
            models.Q(owner=user) | models.Q(owner__isnull=True),
            enabled=True,
        )

    def receiving(self):
        """Return QuerySet with domains that can receive mail"""
        return self.filter(enabled=True)


class InboxQuerySet(QuerySet):
    def create(self, length=settings.INBOX_LENGTH, domain=None, **kwargs):
        """Create a new Inbox, with a local part of `length`"""
        from inboxen.models import Domain

        if not isinstance(domain, Domain):
            raise Domain.DoesNotExist(_("You need to provide a Domain object for an Inbox"))

        while True:
            # loop around until we create a unique address
            inbox = []
            for i in range(length):
                inbox += random.choice(string.ascii_lowercase)

            inbox = "".join(inbox)

            # check against reserved names
            if is_reserved(inbox):
                raise IntegrityError

            try:
                return super(InboxQuerySet, self).create(
                    inbox=inbox,
                    created=datetime.now(utc),
                    domain=domain,
                    **kwargs
                )

            except IntegrityError:
                pass

    def from_string(self, email="", user=None):
        """Returns an Inbox object or raises DoesNotExist"""
        inbox, domain = email.split("@", 1)
        inbox = self.filter(inbox=inbox, domain__domain=domain)

        if user is not None:
            inbox = inbox.filter(user=user)

        inbox = inbox.get()

        return inbox

    def receiving(self):
        """Returns a QuerySet of Inboxes that can receive emails"""
        from inboxen.models import Inbox

        qs = self.filter(domain__enabled=True, user__isnull=False)
        return qs.exclude(
            models.Q(flags=Inbox.flags.deleted) |
            models.Q(flags=Inbox.flags.disabled),
        )

    def viewable(self, user):
        """Returns a QuerySet of Inboxes the user can view"""
        from inboxen.models import Inbox

        qs = self.filter(user=user)
        return qs.exclude(flags=F("flags").bitor(Inbox.flags.deleted))

    def add_last_activity(self):
        """Annotates `last_activity` onto each Inbox and then orders by that column"""
        qs = self.annotate(last_activity=MaxDefault("email__received_date", default="created")).order_by("-last_activity")
        return qs


##
# Email managers
##


class EmailQuerySet(QuerySet):
    def viewable(self, user):
        from inboxen.models import Email, Inbox

        qs = self.filter(inbox__user=user)
        return qs.exclude(
            Q(flags=F("flags").bitor(Email.flags.deleted)) |
            Q(inbox__flags=F("inbox__flags").bitor(Inbox.flags.deleted)),
        )


class HeaderQuerySet(HashedQuerySet):
    def create(self, name=None, data=None, ordinal=None, hashed=None, **kwargs):
        from inboxen.models import HeaderName, HeaderData

        if hashed is None:
            hashed = self.hash_it(data)

        name = HeaderName.objects.only('id').get_or_create(name=name)[0]
        data, created = HeaderData.objects.only('id').get_or_create(hashed=hashed, defaults={'data': data})

        return (super(HeaderQuerySet, self).create(name=name, data=data, ordinal=ordinal, **kwargs), created)

    def get_many(self, *args, **kwargs):
        group_by = kwargs.pop("group_by", None)
        query = models.Q()

        for item in args:
            query = query | models.Q(name__name=item)

        values = self.filter(query)

        if group_by is None:
            values = values.values_list("name__name", "data__data")
            return OrderedDict(values)

        values = values.values_list(group_by, "name__name", "data__data")

        headers = OrderedDict()
        for value in values:
            part = headers.get(value[0], OrderedDict())
            part[value[1]] = value[2]
            headers[value[0]] = part

        return headers


class BodyQuerySet(HashedQuerySet):
    def get_or_create(self, data=None, hashed=None, **kwargs):
        if hashed is None:
            hashed = self.hash_it(data)

        if "defaults" in kwargs:
            kwargs.pop("defaults")

        return super(BodyQuerySet, self).get_or_create(hashed=hashed, defaults={'data': data}, **kwargs)
