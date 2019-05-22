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

from django.contrib.auth import get_user_model
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
