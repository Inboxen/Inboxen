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

from django.core import urlresolvers

from inboxen.test import InboxenTestCase
import redirect


class RedirectTestCase(InboxenTestCase):
    def test_get(self):
        url = urlresolvers.reverse("redirect")
        url = "%s?url=/" % url
        response = self.client.get(url, follow=True)

        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0], "/")
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_proxy_url_no_proto(self):
        url = "/?bizz=iss"
        proxied = redirect.proxy_url(url)

        self.assertEqual("/click/?url=/%3Fbizz%3Diss", proxied)

        response = self.client.get(proxied, follow=True)

        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0], "/?bizz=iss")
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_proxy_url_no_proto_and_port(self):
        url = "localhost:8080"
        proxied = redirect.proxy_url(url)

        self.assertEqual("/click/?url=localhost%3A8080", proxied)

        response = self.client.get(proxied, follow=True)

        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0], "localhost:8080")
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_proxy_url_http_proto(self):
        url = "http://localhost/?bizz=iss"
        proxied = redirect.proxy_url(url)

        self.assertEqual("/click/?url=http%3A//localhost/%3Fbizz%3Diss", proxied)

        response = self.client.get(proxied, follow=True)

        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0], "http://localhost/?bizz=iss")
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_proxy_url_http_proto(self):
        url = "mailto:user@example.com"
        proxied = redirect.proxy_url(url)

        # url should have not changed
        self.assertEqual("mailto:user@example.com", proxied)
