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

class SingleInboxTestCase(test.TestCase):
    """Test Inbox specific views"""
    def setUp(self):
        """Create the client and some inboxes"""
        self.client = test.Client()
        self.client.login(username="isdabizda")
        self.user = models.User.objects.get(username="isdabizda")
        domain = models.Domain.objects.create(domain="localhost")
        self.inbox = models.Inbox.objects.create(domain=domain, user=self.user)

        #TODO: insert emails

    def test_get(self):
        response = self.client.get(urlresolvers.reverse("single-inbox", kwargs={"inbox": self.inbox.inbox, "domain": self.domain.domain}))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        pass

    def test_pagin(self):
        pass
