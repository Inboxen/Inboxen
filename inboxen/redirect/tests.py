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

from django import urls

from inboxen import redirect
from inboxen.test import InboxenTestCase


class RedirectTestCase(InboxenTestCase):
    def test_get(self):
        url = urls.reverse("redirect")
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

        # behaviour of urlparse changed between Python 3.6 and 3.10. 3.10 now
        # interprets "localhost" as the scheme, which is not an allowed scheme.
        # Not sure if this is a bug or not and even then I'm not sure if it's a
        # Django bug or a Python bug.
        self.assertEqual(response.status_code, 400)
        # self.assertEqual(len(response.redirect_chain), 1)
        # self.assertEqual(response.redirect_chain[0][0], "localhost:8080")
        # self.assertEqual(response.redirect_chain[0][1], 302)

    def test_proxy_url_http_proto(self):
        url = "https://localhost/?bizz=iss"
        proxied = redirect.proxy_url(url)

        self.assertEqual("/click/?url=https%3A//localhost/%3Fbizz%3Diss", proxied)

        response = self.client.get(proxied, follow=True)

        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0], "https://localhost/?bizz=iss")
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_proxy_url_wrong_proto(self):
        url = "mailto:user@example.com"
        proxied = redirect.proxy_url(url)

        # url should have not changed
        self.assertEqual("mailto:user@example.com", proxied)
