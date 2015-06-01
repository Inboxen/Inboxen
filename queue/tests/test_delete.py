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

from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import unittest

from inboxen import models
from inboxen.tests import factories
from queue.delete import tasks


class DeleteTestCase(test.TestCase):
    """Test account deleting"""
    def setUp(self):
        self.user = factories.UserFactory()

    def test_delete_account(self):
        factories.EmailFactory.create_batch(10, inbox__user=self.user)
        tasks.delete_account.delay(user_id=self.user.id)

        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(models.Email.objects.count(), 0)
        self.assertEqual(models.Inbox.filter(flags=~models.Inbox.flags.deleted).count(), 0)
        self.assertEqual(models.Inbox.filter(user__isnull=False).count(), 0)

    def test_delete_orphans(self):
        models.Body.objects.get_or_create(data="this is a test")
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

    def test_finish_delete_user(self):
        factories.InboxFactory.create_batch(4, user=self.user)

        with self.assertRaises(Exception):
            tasks.finish_delete_user({}, self.user.id)

        self.user.inbox_set.delete()
        tasks.finish_delete_user({}, self.user.id)

        with self.assertRaises(get_user_model().DoesNotExist):
            get_user_model().objects.get(id=1)

    def test_disown_inbox(self):
        inbox = factories.InboxFactory(user=self.user)
        tasks.disown_inbox.delay({}, inbox.id)

        inbox = models.Inbox.objects.get(id=inbox.id)
        self.assertEqual(inbox.user, None)
