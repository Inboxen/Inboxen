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
from inboxen.utils import unicode_damnit
from router.app.helpers import make_email


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


EXAMPLE_DIGEST = """Content-Type: multipart/mixed; boundary="===============1488510984=="
MIME-Version: 1.0
From: centos-announce-request@centos.org
Subject: CentOS-announce Digest, Vol 109, Issue 3
To: centos-announce@centos.org
Reply-To: centos-announce@centos.org
Date: Mon, 10 Mar 2014 12:00:04 +0000
Message-ID: <mailman.12.1394452804.11046.centos-announce@centos.org>
X-BeenThere: centos-announce@centos.org
X-Mailman-Version: 2.1.9
Precedence: list
List-Id: "CentOS announcements \(security and general\) will be posted to
 this list." <centos-announce.centos.org>
List-Unsubscribe:
 <http://lists.centos.org/mailman/listinfo/centos-announce>, 
 <mailto:centos-announce-request@centos.org?subject=unsubscribe>
List-Archive: <http://lists.centos.org/pipermail/centos-announce>
List-Post: <mailto:centos-announce@centos.org>
List-Help: <mailto:centos-announce-request@centos.org?subject=help>
List-Subscribe: <http://lists.centos.org/mailman/listinfo/centos-announce>,
 <mailto:centos-announce-request@centos.org?subject=subscribe>
Sender: centos-announce-bounces@centos.org
Errors-To: centos-announce-bounces@centos.org
X-Evolution-Source: 1373376044.1477.3@orpheus


--===============1488510984==
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Description: CentOS-announce Digest, Vol 109, Issue 3

Send CentOS-announce mailing list submissions to
        centos-announce@centos.org

To subscribe or unsubscribe via the World Wide Web, visit
        http://lists.centos.org/mailman/listinfo/centos-announce
or, via email, send a message with subject or body 'help' to
        centos-announce-request@centos.org

You can reach the person managing the list at
        centos-announce-owner@centos.org

When replying, please edit your Subject line so it is more specific
than "Re: Contents of CentOS-announce digest..."

--===============1488510984==
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Description: Today's Topics (2 messages)

Today's Topics:

   1. CEBA-2014:0262  CentOS 6 qemu-kvm Update (Johnny Hughes)
   2. CEBA-2014:0264  CentOS 6 libtirpc Update (Johnny Hughes)

--===============1488510984==
Content-Type: multipart/digest; boundary="===============0249781194=="
MIME-Version: 1.0


--===============0249781194==
Content-Type: message/rfc822
MIME-Version: 1.0

From: Johnny Hughes <johnny@centos.org>
Precedence: list
MIME-Version: 1.0
To: centos-announce@centos.org
Date: Mon, 10 Mar 2014 11:21:06 +0000
Reply-To: centos@centos.org
Message-ID: <20140310112106.GA24758@n04.lon1.karan.org>
Content-Type: text/plain; charset=us-ascii
Subject: [CentOS-announce] CEBA-2014:0262  CentOS 6 qemu-kvm Update
Message: 1


CentOS Errata and Bugfix Advisory 2014:0262 

Upstream details at : https://rhn.redhat.com/errata/RHBA-2014-0262.html

The following updated files have been uploaded and are currently 
syncing to the mirrors: ( sha256sum Filename ) 

i386:
46164fd539f764d60217ca6193928d37e8ab3ae1be81ae833b15f866de5fedd0  qemu-guest-agent-0.12.1.2-2.415.el6_5.5.i686.rpm

x86_64:
aed574e07f0992175f9777787991b664d1cf72c8e0d563e7d58185282ce3f8c4  qemu-guest-agent-0.12.1.2-2.415.el6_5.5.x86_64.rpm
0885b34016bdc113d1dff172d9835aec6ae4dc5919243ec7cb707cbebc607527  qemu-img-0.12.1.2-2.415.el6_5.5.x86_64.rpm
01109b5adab7bf10e5b81c670838160e74a60ee75561e971fca378773ff3941a  qemu-kvm-0.12.1.2-2.415.el6_5.5.x86_64.rpm
7e2e6e07951b8611473551f983eabaf60e3a649e8a04cc933ea47aa3b94f0479  qemu-kvm-tools-0.12.1.2-2.415.el6_5.5.x86_64.rpm

Source:
9abd731cd3600b76507b3c1911fc89464c6f29d37b04f349d3a684812e66f402  qemu-kvm-0.12.1.2-2.415.el6_5.5.src.rpm



-- 
Johnny Hughes
CentOS Project { http://www.centos.org/ }
irc: hughesjr, #centos@irc.freenode.net



--===============0249781194==
Content-Type: message/rfc822
MIME-Version: 1.0

From: Johnny Hughes <johnny@centos.org>
Precedence: list
MIME-Version: 1.0
To: centos-announce@centos.org
Date: Mon, 10 Mar 2014 11:21:45 +0000
Reply-To: centos@centos.org
Message-ID: <20140310112145.GA24853@n04.lon1.karan.org>
Content-Type: text/plain; charset=us-ascii
Subject: [CentOS-announce] CEBA-2014:0264  CentOS 6 libtirpc Update
Message: 2


CentOS Errata and Bugfix Advisory 2014:0264 

Upstream details at : https://rhn.redhat.com/errata/RHBA-2014-0264.html

The following updated files have been uploaded and are currently 
syncing to the mirrors: ( sha256sum Filename ) 

i386:
0232079882c8a0f3cdd00417b0fdfc45fdb2f2066d7bd35a2b127658be6f8d94  libtirpc-0.2.1-6.el6_5.1.i686.rpm
0fc6cd31c479c01b3bd4d3a6c62fd04ec8a4429708ef10e41633b628f0771fb4  libtirpc-devel-0.2.1-6.el6_5.1.i686.rpm

x86_64:
0232079882c8a0f3cdd00417b0fdfc45fdb2f2066d7bd35a2b127658be6f8d94  libtirpc-0.2.1-6.el6_5.1.i686.rpm
8fbe3e9cc0f83dd10b6a34c6d37695dccf9968c74177f8cb676467dbd82678fe  libtirpc-0.2.1-6.el6_5.1.x86_64.rpm
0fc6cd31c479c01b3bd4d3a6c62fd04ec8a4429708ef10e41633b628f0771fb4  libtirpc-devel-0.2.1-6.el6_5.1.i686.rpm
9fae583a5e8b1520f5a4982348fa00ce602b0d76e7a01a560e92314f66609385  libtirpc-devel-0.2.1-6.el6_5.1.x86_64.rpm

Source:
1ab0d65c11a4a51a88c7d03884e8f052745fc6778f276731f574ad510dd58185  libtirpc-0.2.1-6.el6_5.1.src.rpm



-- 
Johnny Hughes
CentOS Project { http://www.centos.org/ }
irc: hughesjr, #centos@irc.freenode.net



--===============0249781194==--

--===============1488510984==
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Description: Digest Footer

_______________________________________________
CentOS-announce mailing list
CentOS-announce@centos.org
http://lists.centos.org/mailman/listinfo/centos-announce

--===============1488510984==--
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
        response = self.client.get(self.get_url() + "?imgDisplay=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["email"]["bodies"]), 1)
        content = response.context["email"]["bodies"][0]
        self.assertIn(u"<p>&#160;</p>", content)
        self.assertIn(u"<p>&#163;&#163;&#163;</p>", content)
        self.assertIn(u"http://example.com/coolface.jpg", content)
        self.assertNotIn(u"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=", content)

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
        content = response.context["email"]["bodies"][0]


class UtilityTestCase(test.TestCase):
    def test_is_unicode(self):
        string = "Hey there!"
        self.assertTrue(isinstance(unicode_damnit(string), unicode))

    def test_unicode_passthrough(self):
        already_unicode = u"€"

        # if this doesn't passthrough, it will error
        unicode_damnit(already_unicode, "ascii", "strict")
