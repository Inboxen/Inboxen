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
import itertools

from django import test
from django.conf import settings

from inboxen import models
from inboxen.tests import factories


class ModelTestCase(test.TestCase):
    """Test our custom methods"""
    def test_domain_available(self):
        user = factories.UserFactory()
        other_user = factories.UserFactory(username="lalna")

        # all the permutations of Domains
        for args in itertools.product([True, False], [user, other_user, None]):
            factories.DomainFactory(enabled=args[0], owner=args[1])

        self.assertEqual(models.Domain.objects.available(user).count(), 2)

    def test_inbox_create(self):
        user = factories.UserFactory()
        domain = factories.DomainFactory()

        with self.assertRaises(models.Domain.DoesNotExist):
            models.Inbox.objects.create()

        inbox = models.Inbox.objects.create(domain=domain, user=user)

        self.assertIsInstance(inbox.created, datetime.datetime)
        self.assertEqual(inbox.user, user)

    def test_inbox_from_string(self):
        user = factories.UserFactory()
        other_user = factories.UserFactory(username="lalna")

        inbox = factories.InboxFactory(user=user)
        email = "%s@%s" % (inbox.inbox, inbox.domain.domain)

        inbox2 = user.inbox_set.from_string(email=email)

        self.assertEqual(inbox, inbox2)

        with self.assertRaises(models.Inbox.DoesNotExist):
            other_user.inbox_set.from_string(email=email)

    def test_inbox_receiving(self):
        user = factories.UserFactory()

        # all the permutations of Inboxes that can receive
        params = (
            [True, False],
            [0, models.Inbox.flags.deleted, models.Inbox.flags.disabled,
                models.Inbox.flags.deleted | models.Inbox.flags.disabled,
                ~models.Inbox.flags.deleted & ~models.Inbox.flags.disabled,
            ],
            [user, None],
        )
        for args in itertools.product(*params):
            factories.InboxFactory(domain__enabled=args[0], flags=args[1], user=args[2])

        count = models.Inbox.objects.receiving().count()
        self.assertEqual(count, 2)

    def test_inbox_viewable(self):
        user = factories.UserFactory()
        other_user = factories.UserFactory(username="lalna")

        # all the permutations of Inboxes that can be viewed
        params = (
            [0, models.Inbox.flags.deleted, ~models.Inbox.flags.deleted],
            [user, other_user, None],
        )
        for args in itertools.product(*params):
            factories.InboxFactory(flags=args[0], user=args[1])

        count = models.Inbox.objects.viewable(user).count()
        self.assertEqual(count, 2)

    def test_email_viewable(self):
        user = factories.UserFactory()
        other_user = factories.UserFactory(username="lalna")

        # all the permutations of Emailss that can be viewed
        params = (
            [0, models.Inbox.flags.deleted, ~models.Inbox.flags.deleted],
            [user, other_user, None],
            [0, models.Email.flags.deleted, ~models.Email.flags.deleted],
        )
        for args in itertools.product(*params):
            factories.EmailFactory(inbox__flags=args[0], inbox__user=args[1], flags=args[2])

        count = models.Email.objects.viewable(user).count()
        self.assertEqual(count, 4)

    def test_header_create(self):
        name = "X-Hello"
        data = "Hewwo"
        body = models.Body.objects.create(data="Hello", hashed="fakehash")
        part = models.PartList.objects.create(email=factories.EmailFactory(), body=body)

        header1 = part.header_set.create(name=name, data=data, ordinal=0)
        header2 = part.header_set.create(name=name, data=data, ordinal=1)

        self.assertEqual(header1[0].name_id, header2[0].name_id)
        self.assertEqual(header1[0].data_id, header2[0].data_id)
        self.assertTrue(header1[1])
        self.assertFalse(header2[1])

    def test_body_get_or_create(self):
        body_data = "Hello"

        body1 = models.Body.objects.get_or_create(data=body_data)
        body2 = models.Body.objects.get_or_create(data=body_data)

        self.assertEqual(body1[0].id, body2[0].id)
        self.assertTrue(body1[1])
        self.assertFalse(body2[1])

    def test_requests_are_requested(self):
        user = factories.UserFactory()
        profile = user.userprofile
        profile.pool_amount = settings.MIN_INBOX_FOR_REQUEST
        profile.save()

        profile.available_inboxes()
        self.assertEqual(models.Request.objects.count(), 0)
        factories.InboxFactory(user=user)

        profile.available_inboxes()
        self.assertEqual(models.Request.objects.count(), 1)
        factories.InboxFactory(user=user)

        profile.available_inboxes()
        self.assertEqual(models.Request.objects.count(), 1)
