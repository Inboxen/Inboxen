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

@test.utils.override_settings(CELERY_ALWAYS_EAGER=True)
class SingleInboxTestCase(test.TestCase):
    """Test Inbox specific views"""
    fixtures = ['inboxen_testdata.json']

    def setUp(self):
        """Create the client and some inboxes"""
        self.inbox = models.Inbox.objects.filter(id=1).select_related("user", "domain").get()
        self.user = self.inbox.user

        self.url = urlresolvers.reverse("single-inbox", kwargs={"inbox": self.inbox.inbox, "domain": self.inbox.domain.domain})

        self.client = test.Client()
        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        emails = models.Email.objects.filter(inbox=self.inbox).order_by('-received_date').only("id")
        params = {"read": ""}

        for email in emails[:12]:
            params[email.eid] = "email"

        response = self.client.post(self.url, params)

        self.assertEqual(response.status_code, 302)

    def test_pagin(self):
        # there should be 150 emails in the test fixtures
        # and pages are paginated by 100 items
        response = self.client.get(self.url + "2")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.url + "3")
        self.assertEqual(response.status_code, 404)
