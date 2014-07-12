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

from inboxen import models
from queue.delete import tasks

class DeleteAccountTestCase(test.TestCase):
    """Test account deleting"""
    fixtures = ['inboxen_testdata.json']

    def test_delete(self):
        tasks.delete_account.delay()

        self.assertEqual(models.User.objects.count(), 0)
        self.assertEqual(models.Email.objects.count(), 0)
        self.assertEqual(models.Inbox.filter(flags=~Inbox.flags.deleted).count(), 0)
        self.assertEqual(models.Inbox.filter(user__isnull=False).count(), 0)

class DeleteOrphansTestCase(test.TestCase):
    """Test orphan item deleting"""
    fixtures = ['inboxen_testdata.json']

    def test_delete(self):
        models.Inbox.objects.all().delete()

        tasks.clean_orphan_models.delay()

        self.assertEqual(models.Body.objects.count(), 0)
        self.assertEqual(models.HeaderData.objects.count(), 0)
        self.assertEqual(models.HeaderName.objects.count(), 0)
