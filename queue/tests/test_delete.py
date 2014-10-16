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
from queue.delete import tasks

class DeleteTestCase(test.TestCase):
    """Test account deleting"""
    fixtures = ['inboxen_testdata.json']

    @unittest.skipIf(settings.CELERY_ALWAYS_EAGER, "Task errors during testing, works fine in production")
    def test_delete_account(self):
        tasks.delete_account.delay(user_id=1)

        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(models.Email.objects.count(), 0)
        self.assertEqual(models.Inbox.filter(flags=~Inbox.flags.deleted).count(), 0)
        self.assertEqual(models.Inbox.filter(user__isnull=False).count(), 0)

    @unittest.skipIf(settings.CELERY_ALWAYS_EAGER, "Task errors during testing, works fine in production")
    def test_delete_orphans(self):
        models.Inbox.objects.all().delete()

        tasks.clean_orphan_models.delay()

        self.assertEqual(models.Body.objects.count(), 0)
        self.assertEqual(models.HeaderData.objects.count(), 0)
        self.assertEqual(models.HeaderName.objects.count(), 0)

    def test_delete_inboxen_item(self):
        email = models.Email.objects.only("id").all()[0]
        tasks.delete_inboxen_item.delay("email", email.id)

        with self.assertRaises(models.Email.DoesNotExist):
            models.Email.objects.get(id=email.id)

        # we can send off the same task, but it won't error if there's no object
        tasks.delete_inboxen_item.delay("email", email.id)

        # test with an empty list
        tasks.delete_inboxen_item.chunks([], 500)()

    def test_finish_delete_user(self):
        user = get_user_model().objects.get(id=1)

        with self.assertRaises(Exception):
            tasks.finish_delete_user({}, user.id)

        user.inbox_set.delete()
        tasks.finish_delete_user({}, user.id)

        with self.assertRaises(get_user_model().DoesNotExist):
            get_user_model().objects.get(id=1)

    def test_disown_inbox(self):
        inbox = models.Inbox.objects.filter(user__isnull=False).only("id")[0]
        tasks.disown_inbox.delay({}, inbox.id)

        inbox = models.Inbox.objects.get(id=inbox.id)
        self.assertEqual(inbox.user, None)
