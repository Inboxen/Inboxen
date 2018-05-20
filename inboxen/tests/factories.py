# -*- coding: utf-8 -*-
##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
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

import datetime

from django.contrib.auth import get_user_model
from pytz import utc
from watson import search
import factory
import factory.fuzzy
import six

from inboxen import models


class FuzzyBinary(factory.fuzzy.FuzzyText):
    """Fuzzes a byte string, works the same as FuzzyText"""
    def fuzz(self):
        fuzz = super(FuzzyBinary, self).fuzz()
        return fuzz.encode("utf-8")


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    # Django 1,11 on Python 2 disallows non-ASCII chars in usernames, which is
    # annoying because previous versions did not validate this on the model
    # itself (Inboxen.org has users with non-ascii usernames)
    if six.PY3:
        username = factory.Sequence(lambda n: u"isdabizdå%d" % n)
    else:
        username = factory.Sequence(lambda n: u"isdabizda%d" % n)
    password = "123456"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Call `create_user` rather than `create`

        Happily ignores `django_get_or_create`
        """
        manager = cls._get_manager(model_class)

        return manager.create_user(*args, **kwargs)


class DomainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Domain

    domain = factory.Sequence(lambda n: "example%d.com" % n)


class InboxFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Inbox

    domain = factory.SubFactory(DomainFactory)


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Email

    inbox = factory.SubFactory(InboxFactory)
    received_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2000, 2, 4, tzinfo=utc))


class BodyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Body
        django_get_or_create = ("data", )

    data = FuzzyBinary()


class PartListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PartList

    body = factory.SubFactory(BodyFactory)


class HeaderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Header

    data = factory.fuzzy.FuzzyText()
    name = factory.fuzzy.FuzzyText()
    part = factory.SubFactory(PartListFactory)
    ordinal = factory.Sequence(int)


class FullEmailFactory(EmailFactory):
    """Create a full fleshed out Email object, with a plain text body and some
    headers. It should also produce a search entry
    """
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with search.update_index():
            email = super(FullEmailFactory, cls)._create(model_class, *args, **kwargs)
            body = BodyFactory(data="This mail body is searchable")
            part = PartListFactory(email=email, body=body)
            HeaderFactory(part=part, name="From")
            HeaderFactory(part=part, name="Subject")
            HeaderFactory(part=part, name="Content-Type", data="text/plain; charset=\"ascii\"")

        return email
