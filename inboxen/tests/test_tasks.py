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

from datetime import datetime, timedelta
import itertools

from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
from watson.models import SearchEntry
import mock

from inboxen import models, tasks
from inboxen.tests import factories
from inboxen.test import InboxenTestCase


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

        factories.InboxFactory()
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
            factories.InboxFactory(user=self.user),
            factories.InboxFactory(user=self.user, new=True),
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
    def setUp(self):
        self.user = factories.UserFactory()

    def test_search_empty(self):
        result = tasks.search(self.user.id, "bizz")
        self.assertCountEqual(result.keys(), ["results", "has_next", "has_previous"])
        self.assertEqual(result["results"], [])
        self.assertEqual(result["has_next"], False)
        self.assertEqual(result["has_previous"], False)

    def test_search_results(self):
        inboxes = factories.InboxFactory.create_batch(tasks.SEARCH_PAGE_SIZE, user=self.user, description="bizz")
        factories.InboxFactory.create_batch(tasks.SEARCH_PAGE_SIZE, user=self.user, description="fuzz")
        result = tasks.search(self.user.id, "bizz")
        expected_results = list(SearchEntry.objects.filter(object_id_int__in=[i.id for i in inboxes])
                                .order_by("-id").values_list("id", flat=True))
        self.assertEqual(result["results"], expected_results)
        self.assertEqual(result["has_next"], False)
        self.assertEqual(result["has_previous"], False)
        # just assert that it's some value
        self.assertTrue(result["last"])
        self.assertTrue(result["first"])

        factories.InboxFactory(user=self.user, description="bizz")
        result_2nd = tasks.search(self.user.id, "bizz")
        self.assertNotEqual(result_2nd["results"], expected_results)
        self.assertEqual(result_2nd["has_next"], True)
        self.assertEqual(result_2nd["has_previous"], False)
        # just assert that it's some value
        self.assertTrue(result_2nd["last"])
        self.assertNotEqual(result["last"], result_2nd["last"])
        self.assertTrue(result_2nd["first"])
        self.assertNotEqual(result["first"], result_2nd["first"])

    def test_search_no_results(self):
        factories.InboxFactory.create_batch(tasks.SEARCH_PAGE_SIZE, user=self.user, description="bizz")
        result = tasks.search(self.user.id, "bazz")
        self.assertEqual(result["results"], [])

        # FieldError happens if you try to order by watson_rank when no results were found
        result = tasks.search(self.user.id, "")
        self.assertEqual(result["results"], [])

    def test_after_and_before(self):
        inboxes = factories.InboxFactory.create_batch(tasks.SEARCH_PAGE_SIZE + 3, user=self.user, description="bizz")
        result = tasks.search(self.user.id, "bizz")
        expected_results = list(SearchEntry.objects.filter(object_id_int__in=[i.id for i in inboxes])
                                .order_by("-id").values_list("id", flat=True))

        self.assertEqual(result["results"], expected_results[:-3])
        self.assertEqual(result["has_next"], True)
        self.assertEqual(result["has_previous"], False)
        self.assertNotEqual(result["last"], None)
        self.assertNotEqual(result["first"], None)

        result_2nd = tasks.search(self.user.id, "bizz", after=result["last"])
        self.assertEqual(result_2nd["results"], expected_results[-3:])
        self.assertEqual(result_2nd["has_next"], False)
        self.assertEqual(result_2nd["has_previous"], True)
        self.assertTrue(result_2nd["last"])
        self.assertNotEqual(result["last"], result_2nd["last"])
        self.assertTrue(result_2nd["first"])
        self.assertNotEqual(result["first"], result_2nd["first"])

        result_3rd = tasks.search(self.user.id, "bizz", before=result_2nd["first"])
        self.assertEqual(result_3rd["results"], expected_results[:-3])
        self.assertEqual(result_3rd["has_next"], True)
        self.assertEqual(result_3rd["has_previous"], False)

        self.assertEqual(result["first"], result_3rd["first"])
        self.assertEqual(result["last"], result_3rd["last"])

        # finally, test that we can't use before before and after
        with self.assertRaises(ValueError):
            tasks.search(self.user.id, "bizz", after=result_2nd["first"], before=result["last"])


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
        self.assertEqual(SearchEntry.objects.filter(content_type__model="email").count(), 1)

        tasks.delete_inboxen_item.delay("email", email.id)

        self.assertEqual(SearchEntry.objects.filter(content_type__model="email").count(), 0)

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
            tasks.batch_delete_items("email", args=[12, 14])
            self.assertTrue(mock_qs.filter.called)
            self.assertEqual(mock_qs.filter.call_args, ((12, 14), {}))

        mock_qs = mock.Mock()
        mock_qs.filter.return_value.iterator.return_value = []
        with mock.patch("inboxen.tasks.models.Email.objects.only", return_value=mock_qs):
            tasks.batch_delete_items("email", kwargs={"a": "b"})
            self.assertTrue(mock_qs.filter.called)
            self.assertEqual(mock_qs.filter.call_args, ((), {"a": "b"}))


class AutoDeleteEmailsTaskTestCase(InboxenTestCase):
    def test_task_empty(self):
        tasks.auto_delete_emails.delay()

    def test_task_no_valid_users(self):
        factories.EmailFactory.create_batch(5)
        tasks.auto_delete_emails.delay()
        self.assertEqual(models.Email.objects.count(), 5)

    @mock.patch("inboxen.tasks.batch_delete_items")
    @mock.patch("inboxen.tasks.timezone.now")
    def test_batch_delete_call(self, now_mock, task_mock):
        now_mock.return_value = datetime.utcnow()
        tasks.auto_delete_emails()

        self.assertEqual(task_mock.delay.call_count, 1)
        self.assertEqual(task_mock.delay.call_args, (
            ("email",),
            {"kwargs": {"inbox__user__inboxenprofile__auto_delete": True, "important": False,
                        "received_date__lt": now_mock.return_value - timedelta(days=30)}},
        ))

    def test_task(self):
        params = [
            [True, False],  # important
            [True, False],  # read
            [True, False],  # auto-delete
            [
                # received_date
                timedelta(days=settings.INBOX_AUTO_DELETE_TIME - 1),
                timedelta(days=settings.INBOX_AUTO_DELETE_TIME),
                timedelta(days=settings.INBOX_AUTO_DELETE_TIME + 1),
            ],
        ]

        now = timezone.now()

        for args in itertools.product(*params):
            email = factories.EmailFactory(important=args[0], read=args[1], received_date=now - args[3],
                                           inbox__user=factories.UserFactory())
            email.inbox.user.inboxenprofile.auto_delete = args[2]
            email.inbox.user.inboxenprofile.save()

        self.assertEqual(models.Email.objects.count(), 24)

        tasks.auto_delete_emails.delay()

        # 2/3 of emails will be old enough
        # 1/2 not marked import
        # 1/2 users have auto-deleted enabled
        # therefore 1/6 emails can be deleted
        self.assertEqual(models.Email.objects.count(), 20)
