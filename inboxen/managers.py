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

from collections import OrderedDict
import hashlib

from django.conf import settings
from django.db import IntegrityError, models, transaction
from django.db.models import Max, Q
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.encoding import smart_bytes
from django.utils.translation import ugettext as _

from inboxen.search.models import SearchQuerySet
from inboxen.utils import is_reserved


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


class InboxQuerySet(SearchQuerySet):
    def create(self, length=None, domain=None, **kwargs):
        """Create a new Inbox, with a local part of `length`"""
        from inboxen.models import Domain

        length = length or settings.INBOX_LENGTH
        assert length > 0, "Length must be greater than 0 (zero)"

        if not isinstance(domain, Domain):
            raise Domain.DoesNotExist(_("You need to provide a Domain object for an Inbox"))

        # loop around until we get soemthing unique
        while True:
            inbox = get_random_string(length, settings.INBOX_CHOICES)

            if is_reserved(inbox):
                # inbox is reserved, try again
                continue

            try:
                with transaction.atomic():
                    return super(InboxQuerySet, self).create(
                        inbox=inbox,
                        created=timezone.now(),
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
        qs = self.filter(
            domain__enabled=True,
            user__isnull=False,
            deleted=False,
            disabled=False,
            user__inboxenprofile__quota_percent_usage__lt=100,
            user__inboxenprofile__receiving_emails=True,
        )
        return qs

    def viewable(self, user):
        """Returns a QuerySet of Inboxes the user can view"""
        qs = self.filter(user=user)
        return qs.exclude(deleted=True)

    def add_last_activity(self):
        """Annotates `last_activity` onto each Inbox and then orders by that column"""
        qs = self.annotate(last_activity=Coalesce(Max("email__received_date",
                                                      filter=Q(email__deleted=False)), "created"))
        return qs


##
# Email managers
##


class EmailQuerySet(SearchQuerySet):
    def viewable(self, user):
        qs = self.filter(inbox__user=user)
        return qs.exclude(
            Q(deleted=True) |
            Q(inbox__deleted=True),
        )


class HeaderQuerySet(HashedQuerySet):
    def create(self, name=None, data=None, ordinal=None, hashed=None, **kwargs):
        from inboxen.models import HeaderName, HeaderData

        # remove null "bytes"
        data = data.replace("\x00", "")

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
