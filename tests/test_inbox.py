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

    def test_post_read(self):
        emails = self.get_emails().order_by('-received_date').only("id")
        params = {"read": ""}

        for email in emails[:12]:
            params[email.eid] = "email"

        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 302)

        read_count = emails.filter(flags=models.Email.flags.read).count()
        self.assertEqual(read_count, 12)

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

    def test_pagin(self):
        # there should be 150 emails in the test fixtures
        # and pages are paginated by 100 items
        response = self.client.get(self.get_url() + "2")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.get_url() + "3")
        self.assertEqual(response.status_code, 404)


@test.utils.override_settings(CELERY_ALWAYS_EAGER=True)
class SingleInboxTestCase(InboxTestAbstract, test.TestCase):
    """Test Inbox specific views"""
    def setUp(self):
        self.inbox = models.Inbox.objects.filter(id=1).select_related("domain").get()
        super(SingleInboxTestCase, self).setUp()

    def get_url(self):
        return urlresolvers.reverse("single-inbox", kwargs={"inbox": self.inbox.inbox, "domain": self.inbox.domain.domain})

    def get_emails(self):
        return models.Email.objects.filter(inbox=self.inbox)


@test.utils.override_settings(CELERY_ALWAYS_EAGER=True)
class UnifiedInboxTestCase(InboxTestAbstract, test.TestCase):
    """Test Inbox specific views"""
    def get_url(self):
        return urlresolvers.reverse("unified-inbox")

    def get_emails(self):
        return models.Email.objects.filter(inbox__user=self.user)
