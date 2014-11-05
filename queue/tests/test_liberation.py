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

import os
import os.path
import shutil
import mailbox

from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import unittest

from inboxen import models
from queue.liberate import tasks
from website.forms import LiberationForm

_database_not_psql = settings.DATABASES["default"]["ENGINE"] != 'django.db.backends.postgresql_psycopg2'


class LiberateTestCase(test.TestCase):
    """Test account liberating"""
    fixtures = ['inboxen_testdata.json']

    def setUp(self):
        self.user = get_user_model().objects.get(id=1)
        self.mail_dir = os.path.join(os.getcwd(), "isdabizda")
        mailbox.Maildir(self.mail_dir)

    def tearDown(self):
        shutil.rmtree(self.mail_dir, ignore_errors=True)

    @unittest.skipIf(settings.CELERY_ALWAYS_EAGER, "Task errors during testing, works fine in production")
    def test_liberate(self):
        """Run through all combinations of compressions and mailbox formats"""
        for storage in LiberationForm.STORAGE_TYPES:
            for compression in LiberationForm.COMPRESSION_TYPES:
                form_data = {"storage_type": storage[0], "compression_type": compression[0]}
                form = LiberationForm(self.user, data=form_data)
                self.assertTrue(form.is_valid())
                form.save()

                # TODO: check Liberation model actually has correct archive type

    def test_liberate_inbox(self):
        result = tasks.liberate_inbox(self.mail_dir, 1)
        self.assertIn("folder", result)
        self.assertIn("ids", result)
        self.assertTrue(os.path.exists(os.path.join(self.mail_dir, '.' + result["folder"])))

        email_ids = models.Email.objects.filter(inbox_id=1, flags=~models.Email.flags.deleted).values_list("id", flat=True)
        self.assertItemsEqual(email_ids, result["ids"])

    def test_liberate_message(self):
        inbox = tasks.liberate_inbox(self.mail_dir, 1)["folder"]
        tasks.liberate_message(self.mail_dir, inbox, 1)

        with self.assertRaises(Exception):
            tasks.liberate_message(self.mail_dir, inbox, 10000000)

    @unittest.skipIf(_database_not_psql, "Postgres specific fields are used by this test - sorry!")
    def test_liberate_collect_emails(self):
        tasks.liberate_collect_emails(None, self.mail_dir, {"user": self.user.id, "path": self.mail_dir, "storage_type": "0", "compression_type": "0"})

    def test_liberate_fetch_info(self):
        tasks.liberate_fetch_info(None, {"user": self.user.id, "path": self.mail_dir})

    @unittest.skipIf(_database_not_psql, "Postgres specific fields are used by this test - sorry!")
    def test_liberation_finish(self):
        result_path = os.path.join(self.mail_dir, "result")
        open(result_path, "w").write("a test")
        tasks.liberation_finish(result_path, {"user": self.user.id, "path": self.mail_dir, "storage_type": "0", "compression_type": "0"})


class LiberateNewUserTestCase(test.TestCase):
    """Liberate a new user, with no data"""
    def setUp(self):
        self.user = get_user_model().objects.create(username="atester")
        self.mail_dir = os.path.join(os.getcwd(), "isdabizda")
        mailbox.Maildir(self.mail_dir)

    def tearDown(self):
        shutil.rmtree(self.mail_dir, ignore_errors=True)

    @unittest.skipIf(settings.CELERY_ALWAYS_EAGER, "Task errors during testing, works fine in production")
    def test_liberate(self):
        form = LiberationForm(self.user, data={"storage_type": 0, "compression_type": 0})
        self.assertTrue(form.is_valid())
        form.save()

    def test_liberate_fetch_info(self):
        tasks.liberate_fetch_info(None, {"user": self.user.id, "path": self.mail_dir})

    @unittest.skipIf(_database_not_psql, "Postgres specific fields are used by this test - sorry!")
    def test_liberation_finish(self):
        result_path = os.path.join(self.mail_dir, "result")
        open(result_path, "w").write("a test")
        tasks.liberation_finish(result_path, {"user": self.user.id, "path": self.mail_dir, "storage_type": "0", "compression_type": "0"})
