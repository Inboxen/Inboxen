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

from django.conf import settings
from django.db import IntegrityError, models
from django.utils.encoding import smart_bytes

from inboxen.models import Body, Domain, HeaderName, HeaderData, Inbox, User

class HashedManager(models.Manager):
    def hash_it(self, data):
        hashed = hashlib.new(settings.COLUMN_HASHER)
        hashed.update(smart_bytes(data))
        hashed = "{0}:{1}".format(hashed.name, hashed.hexdigest())

        return hashed

class InboxManager(models.Manager):
    def create(self, domain, length=0, **kwargs):
        """length is ignored currently"""
        #TODO: define default for length with issue #57
        length = 5

        if type(domain) in StringTypes:
            domain = Domain.objects.only('id').get(domain=domain)

        doing = True
        while doing:
            # loop around until we create a unique address
            local_part = ""
            for i in range(length):
                local_part += choice(ascii_lowercase)

            inbox = self.model(inbox=inbox, domain=domain, **kwargs)
            try:
                inbox.save(force_insert=True)
                doing = False
            except IntegrityError:
                doing = True

        return inbox

    def from_string(self, email, user=None, deleted=False):
        """Returns an Inbox object or raises DoesNotExist"""
        inbox, domain = email.split("@", 1)

        inbox = self.filter(inbox=inbox, domain__domain=domain, deleted)

        if type(user) is User:
            inbox = inbox.filter(user=user)

        inbox = inbox.get()

        return inbox
                
##
# Email managers
##

class HeaderManager(HashedManager):
    use_for_related_fields = True
    def create(self, name, data, ordinal, hashed=None, **kwargs):
        if hashed is not None:
            hashed = self.hash_it(data)

        name = HeaderName.objects.only('id').get_or_create(name=name)[0]
        data, created = HeaderData.objects.only('id').get_or_create(hashed=hashed, defaults={'data':data})

        return (super(HeaderManager, self).create(name=name, data=data, ordinal=ordinal, **kwargs), created)

class BodyManager(HashedManager):
    use_for_related_fields = True
    def get_or_create(self, data=None, path=None, hashed=None, **kwargs):
        if hashed is not None:
            if path is not None:
                # look for data in the path
                tpath = open(path, "rb")
                try:
                    data = tpath.read()
                finally:
                    tpath.close()
            hashed = self.hash_it(data)

        return super(BodyManager, self).get_or_create(hashed=hashed, defaults={'path':path, 'data':data}, **kwargs)
