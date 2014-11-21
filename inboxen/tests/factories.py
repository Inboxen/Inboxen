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
import factory
import factory.fuzzy

from inboxen import models


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = "isdabizda"
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

    data = factory.fuzzy.FuzzyText()


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
