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

from datetime import timedelta

from django.core import mail
from django.contrib.sessions.models import Session
from django.utils import timezone
import mock

from inboxen import models, tasks
from inboxen.tests import factories
from inboxen.test import override_settings, InboxenTestCase


class StatsTestCase(InboxenTestCase):
    def test_no_exceptions(self):
        tasks.statistics.delay()

        # run a second time, make sure fetching last stat doesn't cause errors
        tasks.statistics.delay()

    def test_all_zeroes(self):
        tasks.statistics.delay()
        stats = models.Statistic.objects.get()
        for key, value in stats.users.items():
            if key in ["oldest_user_joined"]:
                continue
            self.assertEqual(value, 0, key)

        for key, value in stats.inboxes.items():
            self.assertEqual(value, 0, key)

        for key, value in stats.emails.items():
            self.assertEqual(value, 0, key)

    def test_counts(self):
        # test all the counting is done correctly
        domain = factories.DomainFactory()

        # user 1
        user1 = factories.UserFactory()
        inbox11 = factories.InboxFactory(domain=domain, user=user1)
        inbox12 = factories.InboxFactory(domain=domain, user=user1)
        factories.EmailFactory.create_batch(2, inbox=inbox11)
        factories.EmailFactory.create_batch(2, inbox=inbox12)

        # user 2
        user2 = factories.UserFactory()
        inbox21 = factories.InboxFactory(domain=domain, user=user2)
        inbox22 = factories.InboxFactory(domain=domain, user=user2)
        factories.EmailFactory.create_batch(2, inbox=inbox21)
        factories.EmailFactory.create_batch(2, inbox=inbox22)

        # user 3
        factories.UserFactory()

        tasks.statistics.delay()
        stats = models.Statistic.objects.get()

        self.assertEqual(stats.users["count"], 3)
        self.assertEqual(stats.users["new"], 3)
        self.assertEqual(stats.users["with_inboxes"], 2)

        self.assertEqual(stats.inboxes["inbox_count__sum"], 4)
        self.assertEqual(stats.inboxes["inbox_count__max"], 2)
        self.assertEqual(stats.inboxes["inbox_count__min"], 0)
        self.assertEqual(stats.inboxes["inbox_count__avg"], 4.0/3)

        self.assertEqual(stats.emails["email_count__sum"], 8)
        self.assertEqual(stats.emails["email_count__max"], 2)
        self.assertEqual(stats.emails["email_count__min"], 2)
        self.assertEqual(stats.emails["email_count__avg"], 2)

    def test_running_total(self):
        tasks.statistics.delay()
        stats = models.Statistic.objects.get()
        self.assertEqual(stats.emails["email_count__sum"], 0)
        self.assertEqual(stats.emails["running_total"], 0)

        stats.delete()

        inbox = factories.InboxFactory()
        factories.EmailFactory.create_batch(2)

        # first count
        tasks.statistics.delay()
        stats = models.Statistic.objects.get()
        self.assertEqual(stats.emails["email_count__sum"], 2)
        self.assertEqual(stats.emails["running_total"], 2)

        # running total should not have gone down
        models.Email.objects.first().delete()
        tasks.statistics.delay()
        stats = models.Statistic.objects.latest("date")
        self.assertEqual(stats.emails["email_count__sum"], 1)
        self.assertEqual(stats.emails["running_total"], 2)

        # running total should now increase
        factories.EmailFactory()
        tasks.statistics.delay()
        stats = models.Statistic.objects.latest("date")
        self.assertEqual(stats.emails["email_count__sum"], 2)
        self.assertEqual(stats.emails["running_total"], 3)


class CleanSessionsTestCase(InboxenTestCase):
    def test_sessions_deleted(self):
        Session.objects.create(
            session_key="1234",
            session_data="{}",
            expire_date=timezone.now() - timedelta(1),
        )
        self.assertEqual(Session.objects.count(), 1)
        tasks.clean_expired_session.delay()
        self.assertEqual(Session.objects.count(), 0)


class FlagTestCase(InboxenTestCase):
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


class SearchTestCase(InboxenTestCase):
    def test_search(self):
        user = factories.UserFactory()
        result = tasks.search.delay(user.id, "bizz").get()
        self.assertCountEqual(result.keys(), ["emails", "inboxes"])


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    ADMINS=(("Travis", "ci@example.com"),),
)
class RequestReportTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        self.user.inboxenprofile  # autocreate a profile

        now = timezone.now()

        models.Request.objects.create(amount=200, date=now, succeeded=True, requester=self.user, authorizer=self.user)
        self.waiting = models.Request.objects.create(amount=200, date=now, requester=self.user)

    def test_report(self):
        tasks.requests.delay().get()

        # fetch a fresh copy of the profile
        profile = models.UserProfile.objects.get(pk=self.user.inboxenprofile.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Amount: 200", mail.outbox[0].body)
        self.assertIn("User: %s" % (self.user.username), mail.outbox[0].body)
        self.assertIn("Date:", mail.outbox[0].body)
        self.assertIn("Current: %s" % (profile.pool_amount,), mail.outbox[0].body)

    def test_no_reports(self):
        models.Request.objects.all().delete()

        tasks.requests.delay().get()
        self.assertEqual(len(mail.outbox), 0)


class DeleteTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory()

    def test_delete_orphans(self):
        models.Body.objects.get_or_create(data=b"this is a test")
        models.HeaderName.objects.create(name="bluhbluh")
        models.HeaderData.objects.create(data="bluhbluh", hashed="fakehash")
        tasks.clean_orphan_models.delay()

        self.assertEqual(models.Body.objects.count(), 0)
        self.assertEqual(models.HeaderData.objects.count(), 0)
        self.assertEqual(models.HeaderName.objects.count(), 0)

    def test_delete_inboxen_item(self):
        email = factories.EmailFactory(inbox__user=self.user)
        tasks.delete_inboxen_item.delay("email", email.id)

        with self.assertRaises(models.Email.DoesNotExist):
            models.Email.objects.get(id=email.id)

        # we can send off the same task, but it won't error if there's no object
        tasks.delete_inboxen_item.delay("email", email.id)

        # test with an empty list
        tasks.delete_inboxen_item.chunks([], 500)()

    def test_batch_delete_items(self):
        with self.assertRaises(Exception):
            tasks.batch_delete_items("email")

        mock_qs = mock.Mock()
        mock_qs.filter.return_value.iterator.return_value = []
        with mock.patch("inboxen.tasks.models.Email.objects.only", return_value=mock_qs):
            tasks.batch_delete_items("email", args=[12,14])
            self.assertTrue(mock_qs.filter.called)
            self.assertEqual(mock_qs.filter.call_args, ((12, 14), {}))

        mock_qs = mock.Mock()
        mock_qs.filter.return_value.iterator.return_value = []
        with mock.patch("inboxen.tasks.models.Email.objects.only", return_value=mock_qs):
            tasks.batch_delete_items("email", kwargs={"a":"b"})
            self.assertTrue(mock_qs.filter.called)
            self.assertEqual(mock_qs.filter.call_args, ((), {"a":"b"}))
