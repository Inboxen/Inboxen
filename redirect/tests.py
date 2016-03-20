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

from django import test
from django.core import urlresolvers

import redirect


class RedirectTestCase(test.TestCase):
    def test_get(self):
        url = urlresolvers.reverse("redirect")
        url = "%s?url=/" % url
        response = self.client.get(url, follow=True)

        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0], "/")
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_utils(self):
        url = "/?bizz=iss"
        proxied = redirect.proxy_url(url)

        self.assertEqual("/click/?url=/%3Fbizz%3Diss", proxied)

        response = self.client.get(proxied, follow=True)

        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0], "/?bizz=iss")
        self.assertEqual(response.redirect_chain[0][1], 302)
