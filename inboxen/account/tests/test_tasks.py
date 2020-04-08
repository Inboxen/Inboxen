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
from unittest import mock

from django.contrib.auth import get_user_model
from django.utils import timezone
from pytz import utc

from inboxen import models
from inboxen.account import tasks
from inboxen.test import InboxenTestCase
from inboxen.tests import factories


class DeleteTestCase(InboxenTestCase):
    """Test account deleting"""
    def setUp(self):
        self.user = factories.UserFactory()

    def test_delete_account(self):
        factories.EmailFactory.create_batch(10, inbox__user=self.user)
        tasks.delete_account.delay(user_id=self.user.id)

        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(models.Email.objects.count(), 0)
        self.assertEqual(models.Inbox.objects.filter(deleted=False).count(), 0)
        self.assertEqual(models.Inbox.objects.filter(user__isnull=False).count(), 0)

    def test_disown_inbox(self):
        defaults = {field: models.Inbox._meta.get_field(field).get_default() for field in tasks.INBOX_RESET_FIELDS}

        inbox = factories.InboxFactory(user=self.user, description="hello", disabled=True,
                                       exclude_from_unified=True, new=True, pinned=True)
        inbox.update_search()
        inbox.save()

        # make sure the values we're interested in are actually set to a non-default value
        for field_name in tasks.INBOX_RESET_FIELDS:
            with self.subTest(field_name=field_name):
                self.assertNotEqual(getattr(inbox, field_name), defaults[field_name])

        result = tasks.disown_inbox(inbox.id)
        self.assertTrue(result)

        new_inbox = models.Inbox.objects.get(id=inbox.id)
        self.assertEqual(new_inbox.created, datetime.utcfromtimestamp(0).replace(tzinfo=utc))
        self.assertNotEqual(new_inbox.description, inbox.description)
        self.assertTrue(new_inbox.deleted)
        self.assertEqual(new_inbox.user, None)

        for field_name in tasks.INBOX_RESET_FIELDS:
            with self.subTest(field_name=field_name):
                self.assertEqual(getattr(new_inbox, field_name), defaults[field_name])

        result = tasks.disown_inbox(inbox.id + 12)
        self.assertFalse(result)

    def test_finish_delete_user(self):
        factories.InboxFactory.create_batch(4, user=self.user)

        with self.assertRaises(Exception):
            tasks.finish_delete_user({}, self.user.id)

        self.user.inbox_set.all().delete()
        tasks.finish_delete_user({}, self.user.id)

        with self.assertRaises(get_user_model().DoesNotExist):
            get_user_model().objects.get(id=1)


class SuspendedTestCase(InboxenTestCase):
    @mock.patch("inboxen.account.tasks.timezone.now")
    def test_main_function(self, now_mock):
        now_mock.return_value = timezone.now()
        new_dict = {k: mock.Mock() for k, v in tasks.app.tasks.items()}
        with mock.patch.dict(tasks.app.tasks, new_dict, clear=True):
            tasks.user_suspended()
        call_count_total = 0
        for k, v in new_dict.items():
            call_count_total += v.apply_async.call_count
        self.assertEqual(call_count_total, 4)
        self.assertEqual(new_dict["inboxen.account.tasks.user_suspended_disable_emails"].apply_async.call_count, 1)
        self.assertEqual(new_dict["inboxen.account.tasks.user_suspended_disable_emails"].apply_async.call_args, ((), {
            "kwargs": {"kwargs": {"last_login__range": (now_mock.return_value - timedelta(days=90),
                                                        now_mock.return_value - timedelta(days=180))}},
        }))

        self.assertEqual(new_dict["inboxen.account.tasks.user_suspended_delete_emails"].apply_async.call_count, 1)
        self.assertEqual(new_dict["inboxen.account.tasks.user_suspended_delete_emails"].apply_async.call_args, ((), {
            "kwargs": {"kwargs": {"last_login__range": (now_mock.return_value - timedelta(days=180),
                                                        now_mock.return_value - timedelta(days=360))}},
        }))

        self.assertEqual(new_dict["inboxen.account.tasks.user_suspended_delete_user"].apply_async.call_count, 1)
        self.assertEqual(new_dict["inboxen.account.tasks.user_suspended_delete_user"].apply_async.call_args, ((), {
            "kwargs": {"kwargs": {"last_login__lt": now_mock.return_value - timedelta(days=360)}},
        }))
        self.assertEqual(
            new_dict["inboxen.account.tasks.user_suspended_delete_user_never_logged_in"].apply_async.call_count,
            1,
        )
        self.assertEqual(
            new_dict["inboxen.account.tasks.user_suspended_delete_user_never_logged_in"].apply_async.call_args, ((), {
                "kwargs": {"kwargs": {"last_login__lt": now_mock.return_value - timedelta(days=30)}},
            })
        )

    def test_smoke_test_nothing_to_be_done(self):
        tasks.user_suspended()

    def test_smoke_test_with_data(self):
        now = timezone.now()
        user1 = factories.UserFactory(last_login=now - timedelta(days=30))
        user1.inboxenprofile
        user1_email = factories.EmailFactory(inbox__user=user1)
        user2 = factories.UserFactory(last_login=now - timedelta(days=130))
        user2.inboxenprofile
        user2_email = factories.EmailFactory(inbox__user=user2)
        user3 = factories.UserFactory(last_login=now - timedelta(days=330))
        user3.inboxenprofile
        user3_email = factories.EmailFactory(inbox__user=user3)
        user4 = factories.UserFactory(last_login=now - timedelta(days=430))
        user4.inboxenprofile
        user4_email = factories.EmailFactory(inbox__user=user4)
        user5 = factories.UserFactory(last_login=None, date_joined=now)
        user6 = factories.UserFactory(last_login=None, date_joined=now - timedelta(days=40))
        user7 = factories.UserFactory(last_login=now, date_joined=now - timedelta(days=40))

        tasks.user_suspended()

        user1.inboxenprofile.refresh_from_db()
        self.assertEqual(user1.inboxenprofile.receiving_emails, True)
        user1_email.refresh_from_db()

        user2.inboxenprofile.refresh_from_db()
        self.assertEqual(user2.inboxenprofile.receiving_emails, False)
        user2_email.refresh_from_db()

        user3.inboxenprofile.refresh_from_db()
        # user3 hasn't had receiving_emails set to False because they should
        # have had that done already
        self.assertEqual(user3.inboxenprofile.receiving_emails, True)
        with self.assertRaises(models.Email.DoesNotExist):
            user3_email.refresh_from_db()

        with self.assertRaises(models.UserProfile.DoesNotExist):
            user4.inboxenprofile.refresh_from_db()
        with self.assertRaises(models.Email.DoesNotExist):
            user4_email.refresh_from_db()

        # user5 still exists
        user5.refresh_from_db()

        # user6 does not
        with self.assertRaises(get_user_model().DoesNotExist):
            user6.refresh_from_db()

        # user7 still exists
        user7.refresh_from_db()

    def test_disable_emails(self):
        user1 = factories.UserFactory(last_login=timezone.now())
        user1.inboxenprofile
        user2 = factories.UserFactory()
        user2.inboxenprofile

        tasks.user_suspended_disable_emails(kwargs={"last_login__isnull": True})
        # there should only be one, an exception will be raised otherwise
        profile = models.UserProfile.objects.get(receiving_emails=False)
        self.assertEqual(profile.user, user2)

    @mock.patch("inboxen.account.tasks.delete_inboxen_item")
    def test_delete_emails(self, delete_inboxen_item_mock):
        user1 = factories.UserFactory(last_login=timezone.now())
        user2 = factories.UserFactory()

        factories.EmailFactory(inbox__user=user1)
        user2_email = factories.EmailFactory(inbox__user=user2)

        tasks.user_suspended_delete_emails(kwargs={"last_login__isnull": True})
        self.assertEqual(delete_inboxen_item_mock.chunks.call_count, 1)
        self.assertEqual(delete_inboxen_item_mock.chunks.call_args, (([("email", user2_email.pk)], 500), {}))

    @mock.patch("inboxen.account.tasks.delete_account")
    def test_delete_user(self, delete_account_mock):
        factories.UserFactory(last_login=timezone.now())
        user2 = factories.UserFactory()

        tasks.user_suspended_delete_user(kwargs={"last_login__isnull": True})
        self.assertEqual(delete_account_mock.chunks.call_count, 1)
        self.assertEqual(delete_account_mock.chunks.call_args, (([(user2.pk,)], 500), {}))

    @mock.patch("inboxen.account.tasks.delete_account")
    def test_delete_never_logged_in_user(self, delete_account_mock):
        now = timezone.now()
        factories.UserFactory(date_joined=now - timedelta(days=40), last_login=now)
        user2 = factories.UserFactory(date_joined=now - timedelta(days=40), last_login=None)
        factories.UserFactory(date_joined=now, last_login=None)

        tasks.user_suspended_delete_user_never_logged_in(kwargs={"last_login__lt": now - timedelta(days=30)})
        self.assertEqual(delete_account_mock.chunks.call_count, 1)
        self.assertEqual(delete_account_mock.chunks.call_args, (([(user2.pk,)], 500), {}))
