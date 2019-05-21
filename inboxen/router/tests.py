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

from unittest import mock
import shutil

from django.contrib.auth import get_user_model
from django.db import DatabaseError
from salmon.mail import MailRequest
from salmon.routing import Router
from salmon.server import SMTPError

from inboxen import models
from inboxen.router.app.helpers import make_email
from inboxen.router.app.server import forward_to_admins, process_message
from inboxen.test import InboxenTestCase, override_settings
from inboxen.tests import factories

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
    b"",
    b"Hi,\n\nThis is a plain text message!\n",
    b"",
    b"Last part!\n",
    b"Inside part\n",
    b"Another inside part\n",
]


class RouterTestCase(InboxenTestCase):

    def tearDown(self):
        # clean up log and run dirs
        shutil.rmtree("logs", ignore_errors=True)
        shutil.rmtree("run", ignore_errors=True)

    def test_config_import(self):
        """Very simple test to verify we can import settings module"""
        self.assertNotIn("inboxen.router.app.server", Router.HANDLERS)
        from inboxen.router.config import boot  # noqa
        self.assertIn("inboxen.router.app.server", Router.HANDLERS)

    def test_exceptions(self):
        with self.assertRaises(SMTPError) as error:
            process_message(None, None, None)
        self.assertEqual(error.exception.code, 550)

        with self.assertRaises(SMTPError) as error, \
                mock.patch.object(models.Inbox.objects, "filter", side_effect=DatabaseError):
            process_message(None, None, None)
        self.assertEqual(error.exception.code, 451)

    def test_flag_setting(self):
        user = factories.UserFactory()
        inbox = factories.InboxFactory(user=user)

        with mock.patch("inboxen.router.app.server.make_email") as mock_make_email:
            process_message(None, inbox.inbox, inbox.domain.domain)
        self.assertTrue(mock_make_email.called)

        user = get_user_model().objects.get(id=user.id)
        profile = user.inboxenprofile
        inbox = models.Inbox.objects.get(id=inbox.id)

        self.assertTrue(inbox.new)
        self.assertTrue(profile.unified_has_new_messages)

        # reset some bools
        inbox.new = False
        inbox.exclude_from_unified = True
        inbox.save(update_fields=["new", "exclude_from_unified"])
        profile.unified_has_new_messages = False
        profile.save(update_fields=["unified_has_new_messages"])

        with mock.patch("inboxen.router.app.server.make_email") as mock_make_email:
            process_message(None, inbox.inbox, inbox.domain.domain)
        self.assertTrue(mock_make_email.called)

        user = get_user_model().objects.get(id=user.id)
        profile = user.inboxenprofile
        inbox = models.Inbox.objects.get(id=inbox.id)

        self.assertTrue(inbox.new)
        self.assertFalse(profile.unified_has_new_messages)

    def test_make_email(self):
        inbox = factories.InboxFactory()
        message = MailRequest("locahost", "test@localhost", str(inbox), TEST_MSG)

        make_email(message, inbox)
        self.assertEqual(models.Email.objects.count(), 1)
        self.assertEqual(models.PartList.objects.count(), 6)

        email = models.Email.objects.first()
        self.assertEqual(email.inbox, inbox)
        self.assertNotEqual(email.search_tsv, None)

        bodies = [bytes(part.body.data) for part in
                  models.PartList.objects.select_related("body").order_by("level", "lft")]
        self.assertEqual(bodies, BODIES)

    @override_settings(ADMINS=(("admin", "root@localhost"),))
    def test_forwarding(self):
        with mock.patch("inboxen.router.app.server.Relay") as relay_mock:
            deliver_mock = relay_mock.return_value.deliver
            message = MailRequest("", "", "", "")
            forward_to_admins(message, "user", "example.com")

            self.assertEqual(deliver_mock.call_count, 1)
            self.assertEqual(deliver_mock.call_args[0], (message,))
            self.assertEqual(deliver_mock.call_args[1], {"To": ["root@localhost"], "From": "django@localhost"})

            deliver_mock.reset_mock()
            with mock.patch.object(message, "is_bounce", lambda: True):
                forward_to_admins(message, "user", "example.com")

                self.assertEqual(deliver_mock.call_count, 0)

    def test_routes_deliver_to_inbox(self):
        user = factories.UserFactory()
        inbox = factories.InboxFactory(user=user)
        Router.load(['inboxen.router.app.server'])

        with mock.patch("inboxen.router.app.server.Relay") as relay_mock, \
                mock.patch("inboxen.router.app.server.make_email") as mock_make_email:
            deliver_mock = mock.Mock()
            relay_mock.return_value.deliver = deliver_mock
            message = MailRequest("locahost", "test@localhost", str(inbox), TEST_MSG)
            Router.deliver(message)

            self.assertEqual(mock_make_email.call_count, 1)
            self.assertEqual(relay_mock.call_count, 0)
            self.assertEqual(deliver_mock.call_count, 0)

    def test_routes_deliver_to_admin(self):
        Router.load(['inboxen.router.app.server'])

        with mock.patch("inboxen.router.app.server.Relay") as relay_mock, \
                mock.patch("inboxen.router.app.server.make_email") as mock_make_email:
            deliver_mock = mock.Mock()
            relay_mock.return_value.deliver = deliver_mock
            message = MailRequest("locahost", "test@localhost", "root@localhost", TEST_MSG)
            Router.deliver(message)

            self.assertEqual(mock_make_email.call_count, 0)
            self.assertEqual(relay_mock.call_count, 1)
            self.assertEqual(deliver_mock.call_count, 1)
            self.assertEqual(message, deliver_mock.call_args[0][0])

    def test_routes_deliver_to_not_existing_address(self):
        Router.load(['inboxen.router.app.server'])

        message = MailRequest("locahost", "test@localhost", "root1@localhost", TEST_MSG)
        with self.assertRaises(SMTPError) as excp:
            Router.deliver(message)
        self.assertEqual(excp.exception.code, 550)
        self.assertEqual(excp.exception.message, "No such address")

    def test_routes_deliver_to_admin_raise_smtperror_on_other_errors(self):
        Router.load(['inboxen.router.app.server'])

        with mock.patch("salmon.server.smtplib.SMTP") as smtp_mock:
            smtp_mock.return_value.sendmail.side_effect = Exception()
            message = MailRequest("locahost", "test@localhost", "root@localhost", TEST_MSG)

            with self.assertRaises(SMTPError) as excp:
                Router.deliver(message)
            self.assertEqual(excp.exception.code, 450)
            self.assertEqual(excp.exception.message, "Error while forwarding admin message %s" % id(message))
