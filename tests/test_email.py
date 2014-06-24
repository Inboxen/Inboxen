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
class HomeViewTestCase(test.TestCase):
    fixtures = ['inboxen_testdata.json']

    def setUp(self):
        super(HomeViewTestCase, self).setUp()

        self.email = models.Email.objects.filter(id=1).select_related("inbox", "inbox__domain", "inbox__user").get()
        self.user = self.email.inbox.user

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("email-view", kwargs={
                "inbox": self.email.inbox.inbox,
                "domain": self.email.inbox.domain.domain,
                "id": self.email.eid,
                })

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    #TODO: test body choosing with multipart emails
