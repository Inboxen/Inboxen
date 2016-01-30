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
from django.core.urlresolvers import reverse

import mock

from account import decorators
from inboxen.tests import factories


class AnonRequiredTestCase(test.TestCase):
    def setUp(self):
        self.user = factories.UserFactory()

    def test_anon_decorator(self):
        decorated_function = decorators.anonymous_required(lambda request: request)

        # anon
        request = mock.Mock()
        request.user.is_authenticated.return_value = False

        response = decorated_function(request)
        self.assertEqual(request, response)  # our "view" just returns the request
        self.assertTrue(request.user.is_authenticated.called)

        # logged in
        request = mock.Mock()
        request.user.is_authenticated.return_value = True

        response = decorated_function(request)
        self.assertEqual(response["Location"], reverse("user-home"))
        self.assertTrue(request.user.is_authenticated.called)

        # logged in & custom url
        decorated_function = decorators.anonymous_required(lambda request: request, "/some/url/")
        request = mock.Mock()
        request.user.is_authenticated.return_value = True

        response = decorated_function(request)
        self.assertEqual(response["Location"], "/some/url/")

    def test_urls_logged_in(self):
        urls = [reverse("user-registration"), reverse("user-status"), reverse("user-success"), reverse("user-login")]
        assert self.client.login(username=self.user.username, password="123456")

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response["Location"], reverse("user-home"))

    def test_urls_logged_out(self):
        urls = [reverse("user-registration"), reverse("user-status"), reverse("user-success"), reverse("user-login")]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
