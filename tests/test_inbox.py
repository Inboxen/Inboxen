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
from django.core import urlresolvers

from inboxen import models
from website import forms as inboxen_forms

class InboxTestAbstract(object):
    """An abstract TestCase that won't get picked up by Django's test finder"""
    fixtures = ['inboxen_testdata.json']

    def setUp(self):
        """Create the client and grab the user"""
        super(InboxTestAbstract, self).setUp()
        self.user = models.User.objects.get(id=1)

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_post_important(self):
        emails = self.get_emails().order_by('-received_date').only("id")
        params = {"important": ""}

        i = 0
        for email in emails[:12]:
            params[email.eid] = "email"
            if email.flags.important:
                i = i + 1

        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 302)

        important_count = emails.filter(flags=models.Email.flags.important).count()
        self.assertEqual(important_count, 15-i)

    def test_get_read(self):
        emails = self.get_emails().order_by('-received_date').select_related("inbox", "inbox__domain")

        for email in emails[:12]:
            kwargs = {
                "inbox": email.inbox.inbox,
                "domain": email.inbox.domain.domain,
                "id": email.eid,
                }
            self.client.get(urlresolvers.reverse("email-view", kwargs=kwargs))

        read_count = emails.filter(flags=models.Email.flags.read).count()
        self.assertEqual(read_count, 15)

    def test_post_delete(self):
        email_ids = self.get_emails().order_by('?').only('id')[:5]
        email_ids = [email.eid for email in email_ids]
        count_1st = self.get_emails().count()

        response = self.client.post(self.get_url(), {"delete-single": email_ids.pop()})
        self.assertEqual(response.status_code, 302)

        count_2nd = self.get_emails().count()
        self.assertEqual(count_1st-1, count_2nd)

        params = dict([(email_id, "email") for email_id in email_ids])
        params["delete"] = ""
        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 302)

        count_3rd = self.get_emails().count()
        self.assertEqual(count_2nd-4, count_3rd)

    def test_important_first(self):
        response = self.client.get(self.get_url())
        objs = response.context["page_obj"].object_list[:5]
        objs = [obj.important for obj in objs]

        self.assertEqual(objs, [1,1,1,0,0])

    def test_pagin(self):
        # there should be 150 emails in the test fixtures
        # and pages are paginated by 100 items
        response = self.client.get(self.get_url() + "2")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.get_url() + "3")
        self.assertEqual(response.status_code, 404)


class SingleInboxTestCase(InboxTestAbstract, test.TestCase):
    """Test Inbox specific views"""
    def setUp(self):
        self.inbox = models.Inbox.objects.filter(id=1).select_related("domain").get()
        super(SingleInboxTestCase, self).setUp()

    def get_url(self):
        return urlresolvers.reverse("single-inbox", kwargs={"inbox": self.inbox.inbox, "domain": self.inbox.domain.domain})

    def get_emails(self):
        return models.Email.objects.filter(inbox=self.inbox)


class UnifiedInboxTestCase(InboxTestAbstract, test.TestCase):
    """Test Inbox specific views"""
    def get_url(self):
        return urlresolvers.reverse("unified-inbox")

    def get_emails(self):
        return models.Email.objects.filter(inbox__user=self.user)

class InboxAddTestCase(test.TestCase):
    """Test the add inbox page"""
    fixtures = ['inboxen_testdata.json']

    def setUp(self):
        """Create the client and grab the user"""
        super(InboxAddTestCase, self).setUp()
        self.user = models.User.objects.get(id=1)

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("inbox-add")

    def test_inbox_add_form(self):
        response = self.client.get(self.get_url())
        form = response.context["form"]
        self.assertEqual(isinstance(form, inboxen_forms.InboxAddForm), True)

        self.assertEqual("inbox" in form.fields, False)
        self.assertEqual("domain" in form.fields, True)
        self.assertEqual("tags" in form.fields, True)

    def test_inbox_add(self):
        inbox_count_1st = models.Inbox.objects.count()
        response = self.client.post(self.get_url(), {"domain":"1", "tags":"no tags"})
        self.assertEqual(response.status_code, 302)

        inbox_count_2nd = models.Inbox.objects.count()
        self.assertEqual(inbox_count_1st, inbox_count_2nd-1)

class InboxEditTestCase(test.TestCase):
    """Test the add inbox page"""
    fixtures = ['inboxen_testdata.json']

    def setUp(self):
        """Create the client and grab the user"""
        super(InboxEditTestCase, self).setUp()
        self.user = models.User.objects.get(id=1)
        self.inbox = self.user.inbox_set.select_related("domain")[0]

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("inbox-edit", kwargs={"inbox": self.inbox.inbox, "domain": self.inbox.domain.domain})

    def test_inbox_add_form(self):
        response = self.client.get(self.get_url())
        form = response.context["form"]
        self.assertEqual(isinstance(form, inboxen_forms.InboxEditForm), True)

        self.assertEqual("inbox" in form.fields, False)
        self.assertEqual("domain" in form.fields, False)
        self.assertEqual("tags" in form.fields, True)

    def test_inbox_add(self):
        response = self.client.post(self.get_url(), {"tags":"no tags"})
        self.assertEqual(response.status_code, 302)

        self.assertEqual(models.Inbox.objects.filter(tags="no tags").exists(), True)
