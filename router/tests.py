##
#    Copyright (C) 2015 Jessica Tallon & Matt Molyneaux
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

import mock
import sys

from django import test
from django.contrib.auth import get_user_model
from django.db import DatabaseError

from salmon.mail import MailRequest
from salmon.server import SMTPError
from salmon.routing import Router

from inboxen import models
from inboxen.tests import factories
from router.app.helpers import make_email


TEST_MSG = """From: Test <test@localhost>
To: no-reply@example.com
Subject: This is a subject!
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=inboxenTest

--inboxenTest
Content-Type: text/plain

Hi,

This is a plain text message!

--inboxenTest
Content-Type: multipart/mixed; boundary=secondInboxenTest

--secondInboxenTest
Content-Type: text/plain

Inside part

--secondInboxenTest
Content-Type: text/plain

Another inside part

--secondInboxenTest--

--inboxenTest
Content-Type: text/plain

Last part!

--inboxenTest--
"""

BODIES = [
    "",
    "Hi,\n\nThis is a plain text message!\n",
    "",
    "Last part!\n",
    "Inside part\n",
    "Another inside part\n",
]


class RouterTestCase(test.TestCase):
    def setUp(self):
        sys.path.append("router")

    def tearDown(self):
        sys.path.pop()

    def test_config_import(self):
        """Very simple test to verify we can import settings module"""
        self.assertNotIn("app.server", Router.HANDLERS)
        from config import boot
        self.assertIn("app.server", Router.HANDLERS)

    def test_exceptions(self):
        # import here, that way we don't have to fiddle with sys.path in the global scope
        from router.app.server import START

        with self.assertRaises(SMTPError) as error:
            START(None, None, None)
        self.assertEqual(error.exception.code, 550)

        with self.assertRaises(SMTPError) as error, \
                mock.patch.object(models.Inbox.objects, "filter", side_effect=DatabaseError):
            START(None, None, None)
        self.assertEqual(error.exception.code, 451)

    def test_flag_setting(self):
        # import here, that way we don't have to fiddle with sys.path in the global scope
        from router.app.server import START

        user = factories.UserFactory()
        inbox = factories.InboxFactory(user=user)

        with mock.patch("router.app.server.make_email") as mock_make_email:
            START(None, inbox.inbox, inbox.domain.domain)
        self.assertTrue(mock_make_email.called)

        user = get_user_model().objects.get(id=user.id)
        profile = user.userprofile
        inbox = models.Inbox.objects.get(id=inbox.id)

        self.assertTrue(inbox.flags.new)
        self.assertTrue(profile.flags.unified_has_new_messages)

        # reset some flags
        inbox.flags.new = False
        inbox.flags.exclude_from_unified = True
        inbox.save(update_fields=["flags"])
        profile.flags.unified_has_new_messages = False
        profile.save(update_fields=["flags"])

        with mock.patch("router.app.server.make_email") as mock_make_email:
            START(None, inbox.inbox, inbox.domain.domain)
        self.assertTrue(mock_make_email.called)

        user = get_user_model().objects.get(id=user.id)
        profile = user.userprofile
        inbox = models.Inbox.objects.get(id=inbox.id)

        self.assertTrue(inbox.flags.new)
        self.assertFalse(profile.flags.unified_has_new_messages)

    def test_make_email(self):
        inbox = factories.InboxFactory()
        message = MailRequest("locahost", "test@localhost", str(inbox), TEST_MSG)

        make_email(message, inbox)
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.PartList.objects.count(), 6)

        bodies = [str(part.body.data) for part in models.PartList.objects.select_related("body").order_by("level", "lft")]
        self.assertEqual(bodies, BODIES)
