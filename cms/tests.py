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

import sys

from django import test
from django.conf import settings
from django.core import urlresolvers
from django.core.exceptions import PermissionDenied
from wagtail.wagtailadmin import wagtail_hooks as admin_hooks
from wagtail.wagtailadmin.menu import Menu
import mock

from cms.wagtail_hooks import override_user_urls, remove_user_menu_items
from inboxen.tests import factories, utils
from inboxen.utils import override_settings


class MiddlewareMock(object):
    fail = True

    def process_request(self, request):
        if self.fail:
            raise PermissionDenied()


class AdminTestCase(test.TestCase):
    def setUp(self):
        user = factories.UserFactory(is_superuser=True)

        login = self.client.login(username=user.username, password="123456", request=utils.MockRequest(user))

        if not login:
            raise Exception("Could not log in")

    def test_for_smoke(self):
        with mock.patch("inboxen.middleware.WagtailAdminProtectionMiddleware", MiddlewareMock) as middleware_mock:
            # make sure admin is available and not on fire
            url = urlresolvers.reverse("wagtailadmin_home")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)  # OTP protected

            middleware_mock.fail = False
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_login_redirects(self):
        with mock.patch("inboxen.signals.messages"):
            self.client.logout()

        url = urlresolvers.reverse("wagtailadmin_home")
        response = self.client.get(url, follow=True)
        self.assertEqual(len(response.redirect_chain), 2)
        self.assertEqual(response.request["PATH_INFO"], urlresolvers.reverse("user-login"))


class WagtailHooksTestCase(test.TestCase):
    @override_settings(ENABLE_USER_EDITING=True)
    def test_user_editing_enabled(self):
        # not overriding URLS
        self.assertEqual(override_user_urls(), None)

        admin_hooks.settings_menu = Menu(register_hook_name='register_settings_menu_item')
        menu = Menu(register_hook_name='register_admin_menu_item', construct_hook_name='construct_main_menu')
        menu_html = menu.render_html(mock.Mock())
        self.assertIn("Users", menu_html)
        self.assertIn("Groups", menu_html)

    @override_settings(ENABLE_USER_EDITING=False)
    def test_user_editing_disabled(self):
        # URLs to override user and group editing
        self.assertEqual(len(override_user_urls()), 2)

        admin_hooks.settings_menu = Menu(register_hook_name='register_settings_menu_item')
        menu = Menu(register_hook_name='register_admin_menu_item', construct_hook_name='construct_main_menu')
        menu_html = menu.render_html(mock.Mock())
        self.assertNotIn("Users", menu_html)
        self.assertNotIn("Groups", menu_html)
