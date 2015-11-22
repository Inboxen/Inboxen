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

from django import test
from django.core import urlresolvers
from salmon import mail

from inboxen import models
from inboxen.tests import factories
from inboxen.utils.email import _unicode_damnit
from router.app.helpers import make_email
from inboxen.tests.example_emails import EXAMPLE_ALT, EXAMPLE_DIGEST, EXAMPLE_SIGNED_FORWARDED_DIGEST


BODY = """<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<style type="text/css">
p {color: #ffffff;}
</style>
</head>
<body>
<p>Hello! This is a test of <img src="http://example.com/coolface.jpg"></p>
<p>&nbsp;</p>
<p>£££</p><p><a href="http://example.com/?q=thing">link</a></p>
</body>
</html>
"""


METALESS_BODY = """<html>
<head>
<style type="text/css">
p {color: #ffffff;}
</style>
</head>
<body>
<p>Hello! This is a test of <img src="http://example.com/coolface.jpg"></p>
<p>&nbsp;</p>
<p>$$$</p><p><a href="http://example.com/?q=thing">link</a></p>
</body>
</html>
"""


class EmailViewTestCase(test.TestCase):
    def setUp(self):
        super(EmailViewTestCase, self).setUp()

        self.user = factories.UserFactory()
        self.email = factories.EmailFactory(inbox__user=self.user)
        body = factories.BodyFactory(data=BODY)
        part = factories.PartListFactory(email=self.email, body=body)
        factories.HeaderFactory(part=part, name="From")
        factories.HeaderFactory(part=part, name="Subject")
        factories.HeaderFactory(part=part, name="Content-Type", data="text/html; charset=\"utf-8\"")

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        kwargs = {
            "inbox": self.email.inbox.inbox,
            "domain": self.email.inbox.domain.domain,
            "id": self.email.eid,
        }
        return urlresolvers.reverse("email-view", kwargs=kwargs)

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

        # check that delete button has correct value
        button = "value=\"%s\" name=\"delete-single\""
        button = button % self.email.eid
        self.assertIn(button, response.content)

        # check for no-referrer
        self.assertIn('<meta name="referrer" content="no-referrer">', response.content)

    def test_get_with_headers(self):
        response = self.client.get(self.get_url() + "?all-headers=1")
        self.assertEqual(response.status_code, 200)

        headersfetchall = response.context["headersfetchall"]
        self.assertTrue(headersfetchall)

        response = self.client.get(self.get_url() + "?all-headers=0")
        self.assertEqual(response.status_code, 200)

        headersfetchall = response.context["headersfetchall"]
        self.assertFalse(headersfetchall)

    def test_body_encoding_with_imgDisplay(self):
        self.user.userprofile.flags.ask_images = True
        self.user.userprofile.save()

        response = self.client.get(self.get_url() + "?imgDisplay=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        self.assertFalse(response.context["email"]["ask_images"] and response.context["email"]["has_images"])

        content = response.context["email"]["bodies"][0]
        self.assertIn(u"<p>&#160;</p>", content)
        self.assertIn(u"<p>&#163;&#163;&#163;</p>", content)
        self.assertIn(u"http://example.com/coolface.jpg", content)
        self.assertNotIn(u"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=", content)

        # premailer should have worked fine
        self.assertNotIn(u"Part of this message could not be parsed - it may not display correctly", content)

    def test_body_encoding_without_imgDisplay(self):
        self.user.userprofile.flags.ask_images = True
        self.user.userprofile.save()

        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        self.assertTrue(response.context["email"]["ask_images"] and response.context["email"]["has_images"])

        content = response.context["email"]["bodies"][0]
        self.assertIn(u"<p>&#160;</p>", content)
        self.assertIn(u"<p>&#163;&#163;&#163;</p>", content)
        self.assertNotIn(u"http://example.com/coolface.jpg", content)
        self.assertIn(u"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=", content)

        # premailer should have worked fine
        self.assertNotIn(u"Part of this message could not be parsed - it may not display correctly", content)

    def test_body_no_ask_images(self):
        self.user.userprofile.flags.ask_images = False
        self.user.userprofile.save()

        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        self.assertFalse(response.context["email"]["ask_images"] and response.context["email"]["has_images"])

        content = response.context["email"]["bodies"][0]
        self.assertIn(u"<p>&#160;</p>", content)
        self.assertIn(u"<p>&#163;&#163;&#163;</p>", content)
        self.assertNotIn(u"http://example.com/coolface.jpg", content)
        self.assertIn(u"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=", content)

        # premailer should have worked fine
        self.assertNotIn(u"Part of this message could not be parsed - it may not display correctly", content)

    def test_attachments_get(self):
        part = self.email.parts.get()
        url = urlresolvers.reverse("email-attachment", kwargs={"method": "download", "attachmentid": part.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        important = self.email.flags.important

        params = {"important-toggle": ""}
        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "http://testserver%s" % self.get_url())
        email = models.Email.objects.get(pk=self.email.pk)
        self.assertNotEqual(email.flags.important, important)

        important = not important
        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "http://testserver%s" % self.get_url())
        email = models.Email.objects.get(pk=self.email.pk)
        self.assertNotEqual(email.flags.important, important)

    def test_html_a(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        content = response.context["email"]["bodies"][0]
        self.assertIn(u'<a href="/click/?url=http%3A//example.com/%3Fq%3Dthing" target="_blank">link</a>', content)

    # TODO: test body choosing with multipart emails


class BadEmailTestCase(test.TestCase):
    def setUp(self):
        super(BadEmailTestCase, self).setUp()

        self.user = factories.UserFactory()
        self.email = factories.EmailFactory(inbox__user=self.user)
        body = factories.BodyFactory(data=BODY)
        part = factories.PartListFactory(email=self.email, body=body)
        factories.HeaderFactory(part=part, name="From")
        factories.HeaderFactory(part=part, name="Subject")
        factories.HeaderFactory(part=part, name="Content-Type", data="text/html; charset=\"windows-1252\"")
        factories.HeaderFactory(part=part, name="Content-Disposition", data="inline filename=\"He\n\rl\rlo\n.jpg\"")

        self.email_metaless = factories.EmailFactory(inbox__user=self.user)
        body = factories.BodyFactory(data=METALESS_BODY)
        part = factories.PartListFactory(email=self.email_metaless, body=body)
        factories.HeaderFactory(part=part, name="From")
        factories.HeaderFactory(part=part, name="Subject")
        factories.HeaderFactory(part=part, name="Content-Type", data="text/html; charset=\"ascii\"")

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self, email=None):
        if email is None:
            email = self.email

        kwargs = {
            "inbox": email.inbox.inbox,
            "domain": email.inbox.domain.domain,
            "id": email.eid,
        }
        return urlresolvers.reverse("email-view", kwargs=kwargs)

    def test_body_encoding_with_imgDisplay(self):
        response = self.client.get(self.get_url() + "?imgDisplay=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        content = response.context["email"]["bodies"][0]
        self.assertIn(u"<p>&#160;</p>", content)
        self.assertIn(u"<p>&#163;&#163;&#163;</p>", content)
        self.assertIn(u"http://example.com/coolface.jpg", content)

        # premailer should have worked fine
        self.assertNotIn(u"Part of this message could not be parsed - it may not display correctly", content)

    def test_body_encoding_without_imgDisplay(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        content = response.context["email"]["bodies"][0]
        self.assertIn(u"<p>&#160;</p>", content)
        self.assertIn(u"<p>&#163;&#163;&#163;</p>", content)
        self.assertNotIn(u"http://example.com/coolface.jpg", content)

        # premailer should have worked fine
        self.assertNotIn(u"Part of this message could not be parsed - it may not display correctly", content)

    def test_body_with_no_meta(self):
        response = self.client.get(self.get_url(self.email_metaless) + "?imgDisplay=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        content = response.context["email"]["bodies"][0]
        self.assertIn(u"<p>&#160;</p>", content)
        self.assertIn(u"<p>$$$</p>", content)
        self.assertIn(u"http://example.com/coolface.jpg", content)

        # premailer should have worked fine
        self.assertNotIn(u"Part of this message could not be parsed - it may not display correctly", content)

    def test_attachments_get(self):
        part = self.email.parts.get()
        url = urlresolvers.reverse("email-attachment", kwargs={"method": "download", "attachmentid": part.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("He l lo .jpg", response["Content-Disposition"])

    def test_html_a(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        content = response.context["email"]["bodies"][0]
        self.assertIn(u'<a href="/click/?url=http%3A//example.com/%3Fq%3Dthing" target="_blank">link</a>', content)


class RealExamplesTestCase(test.TestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        self.inbox = factories.InboxFactory(user=self.user)

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        kwargs = {
            "inbox": self.email.inbox.inbox,
            "domain": self.email.inbox.domain.domain,
            "id": self.email.eid,
        }
        return urlresolvers.reverse("email-view", kwargs=kwargs)

    def test_digest(self):
        self.msg = mail.MailRequest("", "", "", EXAMPLE_DIGEST)
        make_email(self.msg, self.inbox)
        self.email = models.Email.objects.get()

        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

        # this email should display all leaves
        leaf_part_count = len([i for i in self.email.get_parts() if i.is_leaf_node()])
        self.assertEqual(len(response.context["email"]["bodies"]), leaf_part_count)

    def test_signed_forwarded_digest(self):
        self.msg = mail.MailRequest("", "", "", EXAMPLE_SIGNED_FORWARDED_DIGEST)
        make_email(self.msg, self.inbox)
        self.email = models.Email.objects.get()

        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

        leaf_part_count = len([i for i in self.email.get_parts() if i.is_leaf_node()])
        self.assertEqual(leaf_part_count, 12)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        self.assertEqual(response.context["email"]["bodies"][0], "<pre>Hello\n</pre>")

    def test_alterative(self):
        self.msg = mail.MailRequest("", "", "", EXAMPLE_ALT)
        make_email(self.msg, self.inbox)
        self.email = models.Email.objects.get()

        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)


class UtilityTestCase(test.TestCase):
    def test_is_unicode(self):
        string = "Hey there!"
        self.assertTrue(isinstance(_unicode_damnit(string), unicode))

    def test_unicode_passthrough(self):
        already_unicode = u"€"

        # if this doesn't passthrough, it will error
        _unicode_damnit(already_unicode, "ascii", "strict")
