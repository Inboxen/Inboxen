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

from datetime import datetime

from django import test
from django.contrib.auth import get_user_model
from django.core import mail

from celery import chain
from pytz import utc

from inboxen import models
from inboxen.tests import factories
from inboxen.utils import override_settings
from queue import tasks


class StatsTestCase(test.TestCase):
    """Test flag tasks"""
    # only testing that it doesn't raise an exception atm
    def test_no_exceptions(self):
        tasks.statistics.delay()


class FlagTestCase(test.TestCase):
    """Test flag tasks"""
    # only testing that it doesn't raise an exception atm
    # TODO: actually test
    def setUp(self):
        super(FlagTestCase, self).setUp()
        self.user = factories.UserFactory()
        self.inboxes = [
            factories.InboxFactory(user=self.user, flags=0),
            factories.InboxFactory(user=self.user, flags=models.Inbox.flags.new),
        ]
        self.emails = factories.EmailFactory.create_batch(10, inbox=self.inboxes[0])
        self.emails.extend(factories.EmailFactory.create_batch(10, inbox=self.inboxes[1]))

    def test_flags_from_unified(self):
        tasks.deal_with_flags.delay([email.id for email in self.emails], user_id=self.user.id)

    def test_flags_from_single_inbox(self):
        tasks.deal_with_flags.delay(
            [email.id for email in self.emails],
            user_id=self.user.id,
            inbox_id=self.inboxes[0].id,
        )


class SearchTestCase(test.TestCase):
    def test_search(self):
        user = factories.UserFactory()
        result = tasks.search.delay(user.id, "bizz").get()
        self.assertItemsEqual(result.keys(), ["emails", "inboxes"])


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    ADMINS=(("Travis", "ci@example.com"),),
)
class RequestReportTestCase(test.TestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        self.user.userprofile  # autocreate a profile

        now = datetime.now(utc)

        models.Request.objects.create(amount=200, date=now, succeeded=True, requester=self.user, authorizer=self.user)
        self.waiting = models.Request.objects.create(amount=200, date=now, requester=self.user)

    def test_fetch(self):
        results = tasks.requests_fetch.delay().get()

        self.assertEqual(len(results), 1)
        self.assertItemsEqual(
            results[0],
            ("id", "amount", "date", "requester__username", "requester__userprofile__pool_amount"),
        )
        self.assertEqual(results[0]["id"], self.waiting.id)

    def test_report(self):
        tasks.requests.delay().get()

        # fetch a fresh copy of the profile
        profile = models.UserProfile.objects.get(pk=self.user.userprofile.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Amount: 200", mail.outbox[0].body)
        self.assertIn("User: %s" % (self.user.username), mail.outbox[0].body)
        self.assertIn("Date:", mail.outbox[0].body)
        self.assertIn("Current: %s" % (profile.pool_amount,), mail.outbox[0].body)

    def test_no_reports(self):
        models.Request.objects.all().delete()

        tasks.requests.delay().get()
        self.assertEqual(len(mail.outbox), 0)
