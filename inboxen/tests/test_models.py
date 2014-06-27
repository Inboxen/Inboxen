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

import datetime

from django import test

from inboxen import models

class ModelTestCase(test.TestCase):
    """Test our custom methods"""
    fixtures = ['inboxen_testdata.json']

    def setUp(self):
        super(ModelTestCase, self).setUp()
        self.user = models.User.objects.get(id=1)

    def test_inbox_create(self):
        with self.assertRaises(models.Domain.DoesNotExist):
            models.Inbox.objects.create()

        domain = models.Domain.objects.get(id=1)
        inbox = models.Inbox.objects.create(domain=domain, user=self.user)

        self.assertIsInstance(inbox.created, datetime.datetime)
        self.assertEqual(inbox.user, self.user)

    def test_inbox_from_string(self):
        inbox = models.Inbox.objects.select_related("domain").get(id=1)
        email = "%s@%s" % (inbox.inbox, inbox.domain.domain)

        inbox2 = inbox.user.inbox_set.from_string(email=email)

        self.assertEqual(inbox, inbox2)

    def test_inbox_from_string_and_user(self):
        user = models.User.objects.create(username="bizz")
        domain = models.Domain.objects.get(id=1)
        inbox = models.Inbox.objects.create(domain=domain, user=user)

        with self.assertRaises(models.Inbox.DoesNotExist):
            self.user.inbox_set.from_string(email="%s@%s" % (inbox.inbox, domain.domain))

    def test_tag_create(self):
        tag = "hello"
        inbox = models.Inbox.objects.get(id=1)

        tag_obj = inbox.tag_set.create(tags=tag)
        self.assertEqual(tag_obj[0].tag, tag)
        self.assertEqual(tag_obj[0].inbox, inbox)

    def test_tag_from_string(self):
        tags = "one, two, three, four, five"
        inbox = models.Inbox.objects.get(id=1)

        tag_objs = inbox.tag_set.create(tags=tags)
        tag_str = ", ".join([tag.tag for tag in tag_objs])

        self.assertEqual(tags, tag_str)
        for tag in tag_objs:
            self.assertEqual(tag.inbox, inbox)

    def test_header_create(self):
        name = "X-Hello"
        data = "Hewwo"
        part = models.PartList.objects.get(id=1)

        header1 = part.header_set.create(name=name, data=data, ordinal=0)
        header2 = part.header_set.create(name=name, data=data, ordinal=1)

        self.assertEqual(header1[0].name_id, header2[0].name_id)
        self.assertEqual(header1[0].data_id, header2[0].data_id)
        self.assertEqual(header1[1], True)
        self.assertEqual(header2[1], False)

    def test_body_get_or_create(self):
        body_data = "Hello"

        body1 = models.Body.objects.get_or_create(data=body_data)
        body2 = models.Body.objects.get_or_create(data=body_data)

        self.assertEqual(body1[0].id, body2[0].id)
        self.assertEqual(body1[1], True)
        self.assertEqual(body2[1], False)
