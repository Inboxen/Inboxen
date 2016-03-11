##
#    Copyright (C) 2014-2015 Jessica Tallon & Matt Molyneaux
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

from StringIO import StringIO
from subprocess import CalledProcessError
import sys

from django import test
from django.conf import settings as dj_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core import urlresolvers
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test.client import RequestFactory

import mock

from inboxen.management.commands import router
from inboxen.middleware import ExtendSessionMiddleware
from inboxen.tests import factories, utils
from inboxen.utils import is_reserved, override_settings
from inboxen.views.error import ErrorView


@override_settings(CACHE_BACKEND="locmem:///")
class LoginTestCase(test.TestCase):
    """Test various login things"""
    def setUp(self):
        super(LoginTestCase, self).setUp()
        self.user = factories.UserFactory()
        cache.clear()

    def test_logout_message(self):
        login = self.client.login(username=self.user.username, password="123456")
        self.assertEqual(login, True)

        response = self.client.get(dj_settings.LOGOUT_URL, follow=True)
        self.assertIn("You are now logged out. Have a nice day!", response.content)

    def test_last_login(self):
        login = self.client.login(username=self.user.username, password="123456")
        self.assertEqual(login, True)

        user = get_user_model().objects.get(id=self.user.id)
        self.assertEqual(user.last_login, None)

    def test_normal_login(self):
        response = self.client.get(urlresolvers.reverse("user-home"))
        self.assertEqual(response.status_code, 302)

        params = {
            "auth-username": self.user.username,
            "auth-password": "123456",
            "login_view-current_step": "auth",
        }
        response = self.client.post(dj_settings.LOGIN_URL, params)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(urlresolvers.reverse("user-home"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["request"].user.is_authenticated())

    def test_ratelimit(self):
        params = {
            "auth-username": self.user.username,
            "auth-password": "bad password",
            "login_view-current_step": "auth",
        }
        response = self.client.post(dj_settings.LOGIN_URL, params)
        self.assertEqual(response.status_code, 200)
        for i in range(100):
            response = self.client.post(dj_settings.LOGIN_URL, params)

        # check we got rejected on bad password
        self.assertEqual(response.status_code, 302)

        # check we still get rejected even with a good password
        params["auth-password"] = "123456"
        response = self.client.post(dj_settings.LOGIN_URL, params)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(urlresolvers.reverse("user-home"))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(urlresolvers.reverse("index"))
        self.assertFalse(response.context["request"].user.is_authenticated())

    def test_no_csrf_cookie(self):
        response = self.client.get(dj_settings.LOGIN_URL)
        self.assertNotIn("csrftoken", response.cookies)
        self.assertIn("sessionid", response.cookies)


class IndexTestCase(test.TestCase):
    def test_index_page(self):
        response = self.client.get(urlresolvers.reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Join", response.content)

        with override_settings(ENABLE_REGISTRATION=False):
            response = self.client.get(urlresolvers.reverse("index"))
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("Join", response.content)

    def test_index_page_logged_in(self):
        user = factories.UserFactory()
        assert self.client.login(username=user.username, password="123456")
        response = self.client.get(urlresolvers.reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Join", response.content)

        with override_settings(ENABLE_REGISTRATION=False):
            response = self.client.get(urlresolvers.reverse("index"))
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("Join", response.content)


class ExtendSessionMiddlewareTestCase(test.TestCase):
    def test_get_set(self):
        user = factories.UserFactory()
        request = utils.MockRequest(user)
        ExtendSessionMiddleware().process_request(request)
        self.assertTrue(request.session.modified)

    def test_with_anon(self):
        user = AnonymousUser()
        request = utils.MockRequest(user)
        ExtendSessionMiddleware().process_request(request)
        self.assertFalse(request.session.modified)


class UtilsTestCase(test.TestCase):
    def test_reserved(self):
        self.assertTrue(is_reserved("root"))
        self.assertFalse(is_reserved("root1"))


class FeederCommandTest(test.TestCase):
    def test_command_errors(self):
        with self.assertRaises(CommandError) as error:
            # too few args
            call_command("feeder")

        with self.assertRaises(CommandError) as error:
            # non-existing mbox
            call_command("feeder", "some_file")
        self.assertEqual(error.exception.message, "No such path: some_file")

        with self.assertRaises(CommandError) as error:
            # non-existing inbox
            call_command("feeder", "some_file", inbox="something@localhost")
        self.assertEqual(error.exception.message, "Address malformed")


class UrlStatsCommandTest(test.TestCase):
    def test_command(self):
        with self.assertRaises(CommandError):
            # too few args
            call_command("url_stats")

        stdin = StringIO()
        stdin.write("/\n")
        stdin.seek(0)
        stdout = StringIO()

        old_in = sys.stdin
        old_out = sys.stdout
        sys.stdin = stdin
        sys.stdout = stdout

        try:
            call_command("url_stats", "-")
        finally:
            sys.stdin = old_in
            sys.stdout = old_out


class RouterCommandTest(test.TestCase):
    def test_command(self):
        with self.assertRaises(CommandError) as error:
            call_command("router")
        self.assertEqual(error.exception.message, "Error: one of the arguments --start --stop --status is required")

    def test_handle(self):
        def func():
            raise OSError

        mgmt_command = router.Command()

        with self.assertRaises(CommandError) as error:
            mgmt_command.handle(cmd=func)
        self.assertEqual(error.exception.message, "OSError from subprocess, salmon is probably not in your path.")

        mgmt_command.stdout = StringIO()
        mgmt_command.handle(cmd=lambda: "test")
        self.assertEqual(mgmt_command.stdout.getvalue(), "test")

    @mock.patch("inboxen.management.commands.router.check_output")
    def test_process_error(self, check_mock):
        check_mock.side_effect = CalledProcessError(-1, "salmon", "test")
        mgmt_command = router.Command()

        output = mgmt_command.salmon_start()
        self.assertEqual(output, ["Exit code -1: test"])

        output = mgmt_command.salmon_status()
        self.assertEqual(output, ["Exit code -1: test"])

        output = mgmt_command.salmon_stop()
        self.assertEqual(output, ["Exit code -1: test"])


class ErrorViewTestCase(test.TestCase):
    def test_view(self):
        view_func = ErrorView.as_view(
            error_message="some message or other",
            error_css_class="some-css-class",
            error_code=499,
            headline="some headline"
        )

        request = RequestFactory().get("/")
        response = view_func(request)

        self.assertEqual(response.status_code, 499)
        self.assertIn("some message or other", response.content)
        self.assertIn("some headline", response.content)
        self.assertIn("some-css-class", response.content)

    def test_misconfigured(self):
        view_obj = ErrorView()

        with self.assertRaises(ImproperlyConfigured):
            view_obj.get_error_message()

        with self.assertRaises(ImproperlyConfigured):
            view_obj.get_error_code()
