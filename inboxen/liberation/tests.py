# -*- coding: utf-8 -*-
##
#    Copyright (C) 2014-2015 Jessica Tallon & Matt Molyneaux
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

from importlib import import_module
from io import BytesIO
import base64
import itertools
import mailbox
import os
import os.path
import quopri
import shutil
import tempfile
import uu

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import urlresolvers
from django.core.urlresolvers import reverse
from salmon import mail

from inboxen import models
from inboxen.tests.example_emails import (
    EXAMPLE_ALT,
    EXAMPLE_DIGEST,
    EXAMPLE_MISSING_CTE,
    EXAMPLE_PREMAILER_BROKEN_CSS,
    EXAMPLE_SIGNED_FORWARDED_DIGEST,
)
from inboxen.tests import factories
from inboxen.test import override_settings, InboxenTestCase, MockRequest
from inboxen.liberation import tasks
from inboxen.liberation.forms import LiberationForm
from inboxen.liberation.utils import make_message, INBOXEN_ENCODING_ERROR_HEADER_NAME
from inboxen.router.app.helpers import make_email


class LiberateTestCase(InboxenTestCase):
    """Test account liberating"""
    def setUp(self):
        self.user = factories.UserFactory()
        self.inboxes = factories.InboxFactory.create_batch(2, user=self.user)
        self.emails = factories.EmailFactory.create_batch(5, inbox=self.inboxes[0])
        self.emails.extend(factories.EmailFactory.create_batch(5, inbox=self.inboxes[1]))

        for email in self.emails:
            part = factories.PartListFactory(email=email)
            factories.HeaderFactory(part=part, name="From")
            factories.HeaderFactory(part=part, name="Subject", data="ßssss!")

        self.tmp_dir = tempfile.mkdtemp()
        self.mail_dir = os.path.join(self.tmp_dir, "isdabizda")
        mailbox.Maildir(self.mail_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_liberate(self):
        """Run through all combinations of compressions and mailbox formats"""
        with override_settings(LIBERATION_PATH=self.tmp_dir):
            for storage, compression in itertools.product(LiberationForm.STORAGE_TYPES,
                                                          LiberationForm.COMPRESSION_TYPES):
                form_data = {"storage_type": str(storage[0]), "compression_type": str(compression[0])}
                form = LiberationForm(self.user, data=form_data)
                self.assertTrue(form.is_valid())
                form.save()

                # delete liberation now we're done with it and refetch user
                models.Liberation.objects.all().delete()
                self.user = get_user_model().objects.get(id=self.user.id)

                # TODO: check Liberation model actually has correct archive type

    def test_liberate_inbox(self):
        result = tasks.liberate_inbox(self.mail_dir, self.inboxes[0].id)
        self.assertIn("folder", result)
        self.assertIn("ids", result)
        self.assertTrue(os.path.exists(os.path.join(self.mail_dir, '.' + result["folder"])))

        email_ids = models.Email.objects.filter(inbox=self.inboxes[0]).values_list("id", flat=True)
        self.assertCountEqual(email_ids, result["ids"])

    def test_liberate_message(self):
        inbox = tasks.liberate_inbox(self.mail_dir, self.inboxes[0].id)["folder"]
        email = self.inboxes[0].email_set.all()[0]
        ret_val = tasks.liberate_message(self.mail_dir, inbox, email.id)
        self.assertEqual(ret_val, None)

        ret_val = tasks.liberate_message(self.mail_dir, inbox, 10000000)
        self.assertEqual(ret_val, hex(10000000)[2:])

    def test_liberate_collect_emails(self):
        tasks.liberate_collect_emails(None, self.mail_dir, {"user": self.user.id, "path": self.mail_dir,
                                                            "tarname": self.mail_dir + ".tar.gz",
                                                            "storage_type": "0", "compression_type": "0"})

    def test_liberate_fetch_info(self):
        tasks.liberate_fetch_info(None, {"user": self.user.id, "path": self.mail_dir})

    def test_liberation_finish(self):
        result_path = os.path.join(self.mail_dir, "result")
        open(result_path, "w").write("a test")
        tasks.liberation_finish(result_path, {"user": self.user.id, "path": self.mail_dir,
                                              "storage_type": "0", "compression_type": "0"})


class LiberateNewUserTestCase(InboxenTestCase):
    """Liberate a new user, with no data"""
    def setUp(self):
        self.user = get_user_model().objects.create(username="atester")

        self.tmp_dir = tempfile.mkdtemp()
        self.mail_dir = os.path.join(self.tmp_dir, "isdabizda")
        mailbox.Maildir(self.mail_dir)

    def tearDown(self):
        shutil.rmtree(self.mail_dir, ignore_errors=True)

    def test_liberate(self):
        with override_settings(LIBERATION_PATH=self.tmp_dir):
            form = LiberationForm(self.user, data={"storage_type": 0, "compression_type": 0})
            self.assertTrue(form.is_valid())
            form.save()

    def test_liberate_fetch_info(self):
        tasks.liberate_fetch_info(None, {"user": self.user.id, "path": self.mail_dir})

    def test_liberation_finish(self):
        result_path = os.path.join(self.mail_dir, "result")
        open(result_path, "w").write("a test")
        tasks.liberation_finish(result_path, {"user": self.user.id, "path": self.mail_dir,
                                              "storage_type": "0", "compression_type": "0"})


class LiberateViewTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("user-liberate")

    def test_form_bad_data(self):
        params = {"storage_type": 180, "compression_type": 180}
        form = LiberationForm(user=self.user, data=params)

        self.assertFalse(form.is_valid())

    def test_form_good_data(self):
        params = {"storage_type": 1, "compression_type": 1}
        form = LiberationForm(user=self.user, data=params)

        self.assertTrue(form.is_valid())

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)


class LiberationDownloadViewTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        self.tmp_dir = tempfile.mkdtemp()

        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

    def test_sendfile_no_liberation(self):
        response = self.client.get(reverse("user-liberate-get"))
        self.assertEqual(response.status_code, 404)

    def test_default_backend(self):
        module = import_module(settings.SENDFILE_BACKEND)
        self.assertTrue(hasattr(module, "sendfile"))  # function that django-senfile
        self.assertTrue(hasattr(module.sendfile, "__call__"))  # callable

    @override_settings(SENDFILE_BACKEND="sendfile.backends.xsendfile")
    def test_sendfile(self):
        with override_settings(LIBERATION_PATH=self.tmp_dir):
            self.user.liberation.path = "test.txt"
            self.user.liberation.save()

            self.assertEqual(os.path.join(self.tmp_dir, "test.txt"), self.user.liberation.path)

            file_obj = open(self.user.liberation.path, "wb")
            file_obj.write(b"hello\n")
            file_obj.close()

            response = self.client.get(reverse("user-liberate-get"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"")
            self.assertEqual(response["Content-Type"], "application/x-gzip")
            self.assertEqual(response["Content-Disposition"], 'attachment; filename="liberated_data.tar.gz"')
            self.assertEqual(response["X-Sendfile"], os.path.join(self.tmp_dir, "test.txt"))


class MakeMessageUtilTestCase(InboxenTestCase):
    """Test that example emails are serialisable"""
    def setUp(self):
        self.user = factories.UserFactory()
        self.inbox = factories.InboxFactory(user=self.user)

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def test_digest(self):
        msg = mail.MailRequest("", "", "", EXAMPLE_DIGEST)
        make_email(msg, self.inbox)
        email = models.Email.objects.get()
        message_object = make_message(email)
        new_msg = mail.MailRequest("", "", "", str(message_object))

        self.assertEqual(len(msg.keys()), len(new_msg.keys()))
        self.assertEqual(len(list(msg.walk())), len(list(new_msg.walk())))

    def test_signed_forwarded_digest(self):
        msg = mail.MailRequest("", "", "", EXAMPLE_SIGNED_FORWARDED_DIGEST)
        make_email(msg, self.inbox)
        self.email = models.Email.objects.get()
        email = models.Email.objects.get()
        message_object = make_message(email)
        new_msg = mail.MailRequest("", "", "", str(message_object))

        self.assertEqual(len(msg.keys()), len(new_msg.keys()))
        self.assertEqual(len(list(msg.walk())), len(list(new_msg.walk())))

    def test_alterative(self):
        msg = mail.MailRequest("", "", "", EXAMPLE_ALT)
        make_email(msg, self.inbox)
        email = models.Email.objects.get()
        message_object = make_message(email)
        new_msg = mail.MailRequest("", "", "", str(message_object))

        self.assertEqual(len(msg.keys()), len(new_msg.keys()))
        self.assertEqual(len(list(msg.walk())), len(list(new_msg.walk())))

    def test_bad_css(self):
        """This test uses an example email that causes issue #47"""
        msg = mail.MailRequest("", "", "", EXAMPLE_PREMAILER_BROKEN_CSS)
        make_email(msg, self.inbox)
        email = models.Email.objects.get()
        message_object = make_message(email)
        new_msg = mail.MailRequest("", "", "", str(message_object))

        self.assertEqual(len(msg.keys()), len(new_msg.keys()))
        self.assertEqual(len(list(msg.walk())), len(list(new_msg.walk())))

    def test_unicode(self):
        """This test uses an example email that contains unicode chars"""
        msg = mail.MailRequest("", "", "", EXAMPLE_MISSING_CTE)
        make_email(msg, self.inbox)
        email = models.Email.objects.get()
        message_object = make_message(email)
        new_msg = mail.MailRequest("", "", "", message_object.as_bytes().decode())

        self.assertEqual(len(msg.keys()), len(new_msg.keys()))
        self.assertEqual(len(list(msg.walk())), len(list(new_msg.walk())))

    def test_encoders_used(self):
        # make message with base64 part, uuencode part, 8bit part, 7bit part,
        # quopri part, and some invalid part
        unicode_body_data = "Hello\n\nHow are you?\nPó på pə pë\n".encode()
        ascii_body_data = "Hello\n\nHow are you?\n".encode()
        email = factories.EmailFactory(inbox=self.inbox)
        unicode_body = factories.BodyFactory(data=unicode_body_data)
        ascii_body = factories.BodyFactory(data=ascii_body_data)
        first_part = factories.PartListFactory(email=email, body=factories.BodyFactory(data=b""))
        factories.HeaderFactory(part=first_part, name="Content-Type",
                                data="multipart/mixed; boundary=\"=-3BRZDE/skgKPPh+RuFa/\"")

        unicode_encodings = {
            "base64": check_base64,
            "quoted-printable": check_quopri,
            "uuencode": check_uu,
            "x-uuencode": check_uu,
            "uue": check_uu,
            "x-uue": check_uu,
        }
        ascii_encodings = {
            "7-bit": check_noop,
            "8-bit": check_noop,
            "9-bit": check_unknown,  # unknown encoding
        }
        encodings = {}
        encodings.update(unicode_encodings)
        encodings.update(ascii_encodings)

        for enc in unicode_encodings.keys():
            part = factories.PartListFactory(email=email, parent=first_part, body=unicode_body)
            factories.HeaderFactory(part=part, name="Content-Type", data="text/plain; name=\"my-file.txt\"")
            factories.HeaderFactory(part=part, name="Content-Transfer-Encoding", data=enc)

        for enc in ascii_encodings.keys():
            part = factories.PartListFactory(email=email, parent=first_part, body=ascii_body)
            factories.HeaderFactory(part=part, name="Content-Type", data="text/plain; name=\"my-file.txt\"")
            factories.HeaderFactory(part=part, name="Content-Transfer-Encoding", data=enc)

        # finally, make a part without content headers
        factories.PartListFactory(email=email, parent=first_part, body=ascii_body)

        # and now export
        message_object = make_message(email)

        for message_part in message_object.walk():
            ct = message_part.get("Content-Type", None)
            cte = message_part.get("Content-Transfer-Encoding", None)
            if ct is None:
                # default is to assume 7-bit
                check_noop(message_part, ascii_body_data)
                self.assertEqual(message_part.get_payload(decode=True), ascii_body_data)
            elif ct.startswith("multipart/mixed"):
                pass
            elif cte in ascii_encodings:
                encodings[cte](message_part, ascii_body_data)
                self.assertEqual(message_part.get_payload(decode=True), ascii_body_data)
            elif cte in unicode_encodings:
                encodings[cte](message_part, unicode_body_data)
                self.assertEqual(message_part.get_payload(decode=True), unicode_body_data)
            else:
                raise AssertionError("Unknown Content-Type or Content-Type-Encoding")

        # check that we can decode the whole lot in one go
        output_bytes = message_object.as_string().encode("ascii")
        self.assertNotEqual(len(output_bytes), 0)
        self.assertEqual(output_bytes.count(b"text/plain; name=\"my-file.txt\""), len(encodings))


def check_noop(msg, data):
    assert msg._payload.encode() == data, "Payload has been transformed"

    assert INBOXEN_ENCODING_ERROR_HEADER_NAME not in msg.keys(), "Unexpected error header"


def check_unknown(msg, data):
    assert msg._payload.encode() == data, "Payload has been transformed"

    assert INBOXEN_ENCODING_ERROR_HEADER_NAME in msg.keys(), "Missing error header"


def check_base64(msg, data):
    assert msg._payload.encode() != data, "Payload has not been transformed"
    try:
        payload = base64.standard_b64decode(msg._payload)
    except TypeError:
        assert False, "Payload could not be decoded"
    assert payload == data, "Decoded payload does not match input data"

    assert INBOXEN_ENCODING_ERROR_HEADER_NAME not in msg.keys(), "Unexpected error header"


def check_quopri(msg, data):
    assert msg._payload.encode() != data, "Payload has not been transformed"
    assert quopri.decodestring(msg._payload) == data, "Payload was not encoded correctly"

    assert INBOXEN_ENCODING_ERROR_HEADER_NAME not in msg.keys(), "Unexpected error header"


def check_uu(msg, data):
    assert msg._payload.encode() != data, "Payload has not been transformed"

    outfile = BytesIO()
    try:
        uu.decode(BytesIO(msg._payload.encode()), outfile)
        payload = outfile.getvalue()
    except uu.Error:
        assert False, "Payload could not be decoded"
    assert payload == data, "Decoded payload does not match input data"

    assert INBOXEN_ENCODING_ERROR_HEADER_NAME not in msg.keys(), "Unexpected error header"
