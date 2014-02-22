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

import hashlib
from random import choice
from string import ascii_lowercase
from types import StringTypes
from datetime import datetime

from django.conf import settings
from django.db import IntegrityError, models
from django.utils.encoding import smart_bytes

from dj_queryset_manager import QuerySetManager, queryset_method
from pytz import utc

class HashedManager(QuerySetManager):
    @queryset_method
    def hash_it(self, data):
        hashed = hashlib.new(settings.COLUMN_HASHER)
        hashed.update(smart_bytes(data))
        hashed = "{0}:{1}".format(hashed.name, hashed.hexdigest())

        return hashed

class InboxManager(QuerySetManager):
    use_for_related_fields = True

    @queryset_method
    def create(self, length=5, **kwargs):
        """length is ignored currently"""
        #TODO: define default for length with issue #57

        while True:
            # loop around until we create a unique address
            local_part = ""
            for i in range(length):
                local_part += choice(ascii_lowercase)

            try:
                return super(type(self), self).create(inbox=local_part, created=datetime.now(utc), **kwargs)
            except IntegrityError:
                pass

    @queryset_method
    def from_string(self, email="", user=None, deleted=False):
        """Returns an Inbox object or raises DoesNotExist"""
        inbox, domain = email.split("@", 1)

        inbox = self.filter(inbox=inbox, domain__domain=domain)

        if deleted is not None:
            inbox = inbox.filter(deleted=deleted)

        if user is not None:
            inbox = inbox.filter(user=user)

        inbox = inbox.get()

        return inbox


class TagManager(QuerySetManager):
    use_for_related_fields = True

    @queryset_method
    def from_string(self, tags, **kwargs):
        """Create Tag objects from string"""
        if "," in tags:
            tags = tags.split(",")
        else:
            tags = tags.split(" ")

        for i, tag in enumerate(tags):
            tag = tag.strip()
            tag = self.create(tag, **kwargs)
            tags[i] = tag

        return tags

##
# Email managers
##

class HeaderManager(HashedManager):
    use_for_related_fields = True

    @queryset_method
    def create(self, name, data, ordinal, hashed=None, **kwargs):
        if hashed is None:
            hashed = self.hash_it(data)

        name_model = self.model.name.field.rel.to
        data_model = self.model.data.field.rel.to

        name = name_model.objects.only('id').get_or_create(name=name)[0]
        data, created = data_model.objects.only('id').get_or_create(hashed=hashed, defaults={'data':data})

        return (super(type(self), self).create(name=name, data=data, ordinal=ordinal, **kwargs), created)

    @queryset_method
    def get_many(self, group_by=None, *args):
        query = Q()
        for item in args:
            query = query | Q(name__name=item)

        values = self.filter(query)
        if group_by is None:
            values = values.value_list("name__name", "data__data")
            return dict(values)

        values = values.value_list(group_by, "name__name", "data__data")

        headers = {}
        for value in values:
            part = headers.get(value[0], {})
            part[value[1]] = value[2]
            headers[value[0]] = part

        return headers

class BodyManager(HashedManager):
    use_for_related_fields = True

    @queryset_method
    def get_or_create(self, data=None, path=None, hashed=None, **kwargs):
        if hashed is None:
            if path is not None:
                # look for data in the path
                tpath = open(path, "rb")
                try:
                    data = tpath.read()
                finally:
                    tpath.close()
            hashed = self.hash_it(data)

        return super(type(self), self).get_or_create(hashed=hashed, defaults={'path':path, 'data':data}, **kwargs)
