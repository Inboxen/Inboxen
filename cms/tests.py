##
#    Copyright (C) 2016 Jessica Tallon & Matt Molyneaux
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
import mock

from inboxen.tests import factories
from inboxen.utils import override_settings


class AdminTestCase(test.TestCase):
    def setUp(self):
        user = factories.UserFactory()
        user.is_superuser = True
        user.save()

        login = self.client.login(username=user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def test_login_redirects(self):
        with mock.patch("inboxen.signals.messages"):
            self.client.logout()

        url = urlresolvers.reverse("wagtailadmin_home")
        response = self.client.get(url, follow=True)
        self.assertEqual(len(response.redirect_chain), 2)
        self.assertEqual(response.request["PATH_INFO"], urlresolvers.reverse("user-login"))

    @override_settings(WAGTAIL_ADMIN_BASE_URL="/someurl", ENABLE_USER_EDITING=False)
    def test_user_editing_disabled(self):
        admin_home = urlresolvers.reverse("wagtailadmin_home")
        response = self.client.get(admin_home)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("users", response.content)
        self.assertNotIn("groups", response.content)

        response = self.client.get(admin_home + "users/")
        self.assertEqual(response.status_code, 404)

        response = self.client.get(admin_home + "groups/")
        self.assertEqual(response.status_code, 404)

    @override_settings(WAGTAIL_ADMIN_BASE_URL="/someurl", ENABLE_USER_EDITING=True)
    def test_user_editing_disabled(self):
        admin_home = urlresolvers.reverse("wagtailadmin_home")
        response = self.client.get(admin_home)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Users", response.content)
        self.assertIn("Groups", response.content)

        response = self.client.get(admin_home + "users/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(admin_home + "groups/")
        self.assertEqual(response.status_code, 200)
