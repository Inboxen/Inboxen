##
#    Copyright (C) 2014, 2015, 2018 Jessica Tallon & Matt Molyneaux
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

from datetime import datetime, timedelta
from email.message import Message
from importlib import reload
from io import StringIO
from unittest import mock
import ipaddress
import sys

from django import urls
from django.conf import settings as dj_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.test.client import RequestFactory
from django.utils import timezone

from inboxen.management.commands import feeder, url_stats
from inboxen.middleware import ExtendSessionMiddleware, MakeXSSFilterChromeSafeMiddleware
from inboxen.models import Domain
from inboxen.test import InboxenTestCase, MockRequest, SecureClient
from inboxen.tests import factories
from inboxen.utils import ip, is_reserved, ratelimit
from inboxen.validators import ProhibitNullCharactersValidator
from inboxen.views.error import ErrorView


def reload_urlconf():
    """
    Reload url conf

    Make sure to use clear_url_caches along with this
    """
    if dj_settings.ROOT_URLCONF in sys.modules:
        conf = reload(sys.modules[dj_settings.ROOT_URLCONF])
    else:
        from inboxen import urls as conf

    return conf


class LoginTestCase(InboxenTestCase):
    """Test various login things"""
    def setUp(self):
        super(LoginTestCase, self).setUp()
        self.user = factories.UserFactory()
        cache.clear()

    def tearDown(self):
        super(LoginTestCase, self).tearDown()
        cache.clear()

    def test_logout_message(self):
        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))
        self.assertEqual(login, True)

        response = self.client.get(dj_settings.LOGOUT_URL, follow=True)
        self.assertIn("You are now logged out. Have a nice day!", str(response.content))

    def test_last_login(self):
        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))
        self.assertEqual(login, True)

        user = get_user_model().objects.get(id=self.user.id)
        self.assertNotEqual(user.last_login, None)

    def test_normal_login(self):
        response = self.client.get(urls.reverse("user-home"))
        self.assertEqual(response.status_code, 302)

        params = {
            "auth-username": self.user.username,
            "auth-password": "123456",
            "login_view-current_step": "auth",
        }
        response = self.client.post(dj_settings.LOGIN_URL, params)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(urls.reverse("user-home"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["request"].user.is_authenticated)

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

        response = self.client.get(urls.reverse("user-home"))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(urls.reverse("index"))
        self.assertFalse(response.context["request"].user.is_authenticated)

    def test_no_csrf_cookie(self):
        response = self.client.get(dj_settings.LOGIN_URL)
        self.assertNotIn("csrftoken", response.cookies)
        self.assertIn("sessionid", response.cookies)


class IndexTestCase(InboxenTestCase):
    def test_index_page(self):
        response = self.client.get(urls.reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Join", str(response.content))

        with override_settings(ENABLE_REGISTRATION=False):
            response = self.client.get(urls.reverse("index"))
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("Join", str(response.content))

    def test_index_page_logged_in(self):
        user = factories.UserFactory()
        assert self.client.login(username=user.username, password="123456", request=MockRequest(user))

        response = self.client.get(urls.reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Join", str(response.content))

        with override_settings(ENABLE_REGISTRATION=False):
            response = self.client.get(urls.reverse("index"))
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("Join", str(response.content))


class ExtendSessionMiddlewareTestCase(InboxenTestCase):
    middleware = ExtendSessionMiddleware()

    def test_cycle_session_expires_more_than_week_left(self):
        user = factories.UserFactory()
        request = MockRequest(user)
        request.session.save(must_create=True)

        session_obj = request.session._get_session_from_db()
        session_obj.expire_date = timezone.now() + timedelta(days=10)
        session_obj.save()
        session_key = request.session.session_key
        self.middleware.process_request(request)
        self.assertEqual(request.session.session_key, session_key)
        user.refresh_from_db()
        self.assertEqual(user.last_login, None)

    def test_cycle_session_week_left(self):
        user = factories.UserFactory()
        request = MockRequest(user)
        request.session.save(must_create=True)

        session_obj = request.session._get_session_from_db()
        session_obj.expire_date = timezone.now() + timedelta(days=8)
        session_obj.save()
        session_key = request.session.session_key
        self.middleware.process_request(request)
        self.assertEqual(request.session.session_key, session_key)
        user.refresh_from_db()
        self.assertEqual(user.last_login, None)

    def test_cycle_session_less_than_week_left(self):
        user = factories.UserFactory()
        request = MockRequest(user)
        request.session.save(must_create=True)

        session_obj = request.session._get_session_from_db()
        session_obj.expire_date = timezone.now() + timedelta(days=3)
        session_obj.save()
        session_key = request.session.session_key
        self.middleware.process_request(request)
        self.assertNotEqual(request.session.session_key, session_key)
        user.refresh_from_db()
        self.assertNotEqual(user.last_login, None)

    def test_cycle_session_no_cycle(self):
        user = factories.UserFactory()
        request = MockRequest(user)
        request.session.save(must_create=True)

        session_key = request.session.session_key
        self.middleware.process_request(request)
        self.assertEqual(request.session.session_key, session_key)

    def test_last_login(self):
        user = factories.UserFactory()
        request = MockRequest(user)
        request.session.save(must_create=True)

        # no change, so no last_login
        self.middleware.process_request(request)
        user.refresh_from_db()
        self.assertEqual(user.last_login, None)

    def test_with_anon(self):
        user = AnonymousUser()
        request = MockRequest(user)
        self.middleware.process_request(request)
        self.assertFalse(request.session.modified)


class UtilsTestCase(InboxenTestCase):
    def test_reserved(self):
        self.assertTrue(is_reserved("root"))
        self.assertFalse(is_reserved("root1"))


class FeederCommandTest(InboxenTestCase):
    class MboxMock(dict):
        def __init__(self, *args, **kwargs):
            self._removed = {}
            dict.__init__(self, *args, **kwargs)

        def lock(self):
            self._locked = True

        def close(self):
            self._locked = False

        def remove(self, key):
            self._removed[key] = self[key]
            del self[key]

    @mock.patch("inboxen.management.commands.feeder.smtplib.SMTP")
    def test_command(self, smtp_mock):
        messages = self.MboxMock()
        messages["a"] = Message()
        messages["a"]["To"] = "me@exmaple.com"
        messages["a"]["From"] = "me@exmaple.com"

        with mock.patch("inboxen.management.commands.feeder.mailbox.mbox") as mock_box:
            mock_box.return_value = messages
            call_command("feeder", "/")

    @mock.patch("inboxen.management.commands.feeder.smtplib.SMTP")
    def test_command_inbox(self, smtp_mock):
        inbox = factories.InboxFactory()

        messages = self.MboxMock()
        messages["a"] = Message()
        messages["a"]["To"] = "me@exmaple.com"
        messages["a"]["From"] = "me@exmaple.com"
        # if you specify an inbox, you don't need a To header
        messages["b"] = Message()
        messages["b"]["From"] = "me@exmaple.com"

        with mock.patch("inboxen.management.commands.feeder.mailbox.mbox") as mock_box:
            mock_box.return_value = messages
            call_command("feeder", "/", inbox=str(inbox))

    def test_command_errors(self):
        with self.assertRaises(CommandError) as error:
            # too few args
            call_command("feeder")

        with self.assertRaises(CommandError) as error:
            # non-existing mbox
            call_command("feeder", "some_file")
        self.assertEqual(str(error.exception), "No such path: some_file")

        with self.assertRaises(CommandError) as error:
            # non-existing inbox
            call_command("feeder", "some_file", inbox="something@localhost")
        self.assertEqual(str(error.exception), "Inbox does not exist")

        with mock.patch("inboxen.management.commands.feeder.mailbox.mbox") as mock_box:
            mock_box.return_value = mock.Mock()
            mock_box.return_value.__len__ = lambda x: 0

            with self.assertRaises(CommandError) as error:
                call_command("feeder", "/")
            self.assertEqual(str(error.exception), "Your mbox is empty!")

    def test_get_address(self):
        mgmt_command = feeder.Command()

        address = mgmt_command._get_address("myself <me@example.com>")
        self.assertEqual(address, "<me@example.com>")

        address = mgmt_command._get_address("you@example.com")
        self.assertEqual(address, "<you@example.com>")

        with self.assertRaises(CommandError):
            mgmt_command._get_address("me <>")

    @mock.patch("inboxen.management.commands.feeder.smtplib.LMTP")
    @mock.patch("inboxen.management.commands.feeder.smtplib.SMTP")
    def test_get_server(self, smtp_mock, lmtp_mock):
        mgmt_command = feeder.Command()

        self.assertEqual(mgmt_command._server, None)
        server = mgmt_command._get_server()
        self.assertEqual(mgmt_command._server, server)
        self.assertTrue(smtp_mock.called)
        self.assertFalse(lmtp_mock.called)

        smtp_mock.reset_mock()
        lmtp_mock.reset_mock()
        mgmt_command._server = None

        with self.settings(SALMON_SERVER={"type": "lmtp", "path": "/fake/path"}):
            server = mgmt_command._get_server()
            self.assertEqual(mgmt_command._server, server)
            self.assertTrue(lmtp_mock.called)
            self.assertFalse(smtp_mock.called)


class UrlStatsCommandTest(InboxenTestCase):
    def test_command(self):
        with self.assertRaises(CommandError):
            # too few args
            call_command("url_stats")

        stdin = StringIO()
        stdin.write("/\n/\n")
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

        self.assertTrue(len(stdout.getvalue()) > 0)

    def test_count_urls(self):
        mgmt_command = url_stats.Command()

        url_list = StringIO()
        url_list.write("%s\n" % urls.reverse("single-inbox", kwargs={"inbox": "123", "domain": "example.com"}))
        url_list.write("%s\n" % urls.reverse("single-inbox", kwargs={"inbox": "321", "domain": "example.com"}))
        url_list.write("%s\n" % urls.reverse("unified-inbox"))
        url_list.write("/dfsdfsdf/sdfsdss/111\n")
        url_list.write("%s\n" % urls.reverse("unified-inbox"))
        url_list.write("%s\n" % urls.reverse("unified-inbox"))
        url_list.seek(0)

        returned_urls, non_matches = mgmt_command.count_urls(url_list)

        self.assertEqual(len(returned_urls), 2)
        self.assertEqual(len(non_matches), 1)

        self.assertEqual(returned_urls["single-inbox"], 2)
        self.assertEqual(returned_urls["unified-inbox"], 3)


class CreateDomainCommandTestCase(InboxenTestCase):
    def test_too_few_args(self):
        with self.assertRaises(CommandError):
            call_command("createdomain")

    def test_new_domain(self):
        self.assertEqual(Domain.objects.count(), 0)
        call_command("createdomain", "localhost1")

        domain = Domain.objects.first()
        self.assertEqual(domain.domain, "localhost1")
        self.assertEqual(domain.enabled, True)

    def test_duplicate_domain(self):
        Domain.objects.create(domain="localhost1")
        with self.assertRaises(CommandError):
            call_command("createdomain", "localhost1")


class ErrorViewTestCase(InboxenTestCase):
    def test_view(self):
        view_func = ErrorView.as_view(
            error_message="some message or other",
            error_code=499,
            headline="some headline"
        )

        request = RequestFactory().get("/")
        response = view_func(request)

        self.assertEqual(response.status_code, 499)
        self.assertIn("some message or other", str(response.content))
        self.assertIn("some headline", str(response.content))

    def test_misconfigured(self):
        view_obj = ErrorView()

        with self.assertRaises(ImproperlyConfigured):
            view_obj.get_error_message()

        with self.assertRaises(ImproperlyConfigured):
            view_obj.get_error_code()


class StyleguideTestCase(InboxenTestCase):
    def tearDown(self):
        # make sure URLConf is reset no matter what
        urls.clear_url_caches()
        reload_urlconf()

    def test_get(self):
        # make sure it's accessible when DEBUG=True
        with override_settings(DEBUG=True):
            urls.clear_url_caches()
            reload_urlconf()
            url = urls.reverse('inboxen-styleguide')
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # make sure it's not accessible when DEBUG=False
        with override_settings(DEBUG=False):
            urls.clear_url_caches()
            reload_urlconf()
            # url should no longer exist
            response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ProhibitNullCharactersValidatorTestCase(InboxenTestCase):
    def test_null(self):
        validator = ProhibitNullCharactersValidator()
        with self.assertRaises(ValidationError):
            validator("some \x00text")

    def test_not_null(self):
        validator = ProhibitNullCharactersValidator()
        self.assertIsNone(validator("some text"))

    def test_None(self):
        validator = ProhibitNullCharactersValidator()
        self.assertIsNone(validator(None))

    def test_unicode(self):
        validator = ProhibitNullCharactersValidator()
        self.assertIsNone(validator(u"\ufffd"))


class SSLRedirectTestCase(InboxenTestCase):
    def test_redirect(self):
        response = self.client.get("/", secure=False)
        self.assertEqual(response.status_code, 301)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class CSRFCheckedTestCase(InboxenTestCase):
    def setUp(self):
        self.client = SecureClient(enforce_csrf_checks=True)
        self.url = urls.reverse('user-registration')

    def test_csrf_token_missing(self):
        data = {
            "username": "new_user",
            "password1": "bob1",
            "password2": "bob2",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 403)

    def test_csrf_cookie_not_present(self):
        response = self.client.get(self.url)

        # no csrftokenmiddleware cookie
        self.assertEqual(list(response.cookies.keys()), ["sessionid"])

        # if we move back to cookie based csrf, uncomment these tests
        # self.assertEqual(response.cookies["csrfmiddlewaretoken"]["secure"], True)
        # self.assertEqual(response.cookies["csrfmiddlewaretoken"]["httponly"], True)

    def test_csrf_referer_check(self):
        self.client.get(self.url)  # generate token in session
        data = {
            "username": "new_user",
            "password1": "bob1",
            "password2": "bob2",
            "csrfmiddlewaretoken": self.client.session["_csrftoken"],
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 403)

    def test_csrf_token_present(self):
        self.client.get(self.url)  # generate token in session
        data = {
            "username": "new_user",
            "password1": "bob1",
            "password2": "bob2",
            "csrfmiddlewaretoken": self.client.session["_csrftoken"],
        }

        response = self.client.post(self.url, data, HTTP_REFERER="https://testserver")
        self.assertEqual(response.status_code, 200)


class MakeXSSFilterChromeSafeMiddlewareTestCase(InboxenTestCase):
    def test_middleware_before_security_middleware(self):
        middleware = MakeXSSFilterChromeSafeMiddleware()
        request = None  # ignored
        response = {}  # "mock" header dict

        response = middleware.process_response(request, response)
        self.assertEqual(response["x-xss-protection"], "0")

    def test_middleware_after_security_middleware(self):
        middleware = MakeXSSFilterChromeSafeMiddleware()
        request = None  # ignored
        response = {"x-xss-protection": "1; mode=block"}  # "mock" header dict

        response = middleware.process_response(request, response)
        self.assertEqual(response["x-xss-protection"], "0")

    def test_response(self):
        response = self.client.get("/")
        self.assertEqual(response["x-xss-protection"], "0")


class HSTSTestCase(InboxenTestCase):
    def test_hsts_header(self):
        response = self.client.get("/")
        self.assertEqual(response["strict-transport-security"], "max-age=31536000; includeSubDomains; preload")


@override_settings(SESSION_SAVE_EVERY_REQUEST=True)
class SecureSessionCookieTestCase(InboxenTestCase):
    def test_secure(self):
        # session cookie won't get saved regardless of setting if session is empty
        self.client.session["test"] = "test"

        response = self.client.get("/", secure=False)
        self.assertEqual(response.cookies.output(), "")

        response = self.client.get("/")
        self.assertEqual(response.cookies["sessionid"]["secure"], True)

    def test_httponly(self):
        # session cookie won't get saved regardless of setting if session is empty
        self.client.session["test"] = "test"

        response = self.client.get("/")
        self.assertEqual(response.cookies["sessionid"]["httponly"], True)


class XFrameOptionsTestCase(InboxenTestCase):
    def test_x_frame_options_header(self):
        response = self.client.get("/")
        self.assertEqual(response["x-frame-options"], "DENY")


class XContentTypeOptionsTestCase(InboxenTestCase):
    # no sniffles!
    def test_x_content_type_options(self):
        response = self.client.get("/")
        self.assertEqual(response["x-content-type-options"], "nosniff")


class ManifestTestCase(InboxenTestCase):
    def test_get(self):
        url = urls.reverse('inboxen-manifest')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class IpUtilsTestCase(InboxenTestCase):
    def test_not_ip(self):
        with self.assertRaises(ValueError):
            # ipaddress should raise a ValueError exception
            ip.strip_ip(u"inboxen")

        with self.assertRaises(ValueError), \
                mock.patch("inboxen.utils.ip.ipaddress.ip_address") as ip_mock:
            # Mock is not an instance of IPv4Address or IPv6Address, so our
            # code should raise its own ValueError
            ip.strip_ip("")

        self.assertEqual(ip_mock.call_count, 1)

    def test_ipv4(self):
        filled_ip_addr = "255.255.255.255"
        for i in range(33):
            netmask = (2**32 - 2**i)

            expected_address = ipaddress.ip_address(netmask)
            self.assertEqual(ip.strip_ip(filled_ip_addr, ipv4_host_class=32 - i), str(expected_address))

    def test_ipv6(self):
        filled_ip_addr = "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"
        for i in range(129):
            netmask = 2**128 - 2**i

            expected_address = ipaddress.ip_address(netmask)
            self.assertEqual(ip.strip_ip(filled_ip_addr, ipv6_host_class=128 - i), str(expected_address))


class RateLimitTestCase(InboxenTestCase):
    def setUp(self):
        self.window = 30
        self.limit_count = 10
        self.make_key = lambda x, y: "test-cachekey-%s" % y.date()

        self.limiter = ratelimit.RateLimit(
            self.make_key,
            lambda x: None,
            self.window,
            self.limit_count,
        )

        cache.clear()

    def test_cache_expires_is_set(self):
        self.assertEqual(self.limiter.cache_expires, (self.window + 1) * 60)

    @mock.patch("inboxen.utils.ratelimit.timezone.now")
    def test_check_doesnt_increase_count_if_not_full(self, now_mock):
        now_mock.return_value = datetime.utcnow()
        request = MockRequest()
        request.META["REMOTE_ADDR"] = "127.0.0.1"

        self.limiter.counter_full(request)

        self.assertEqual(len(cache._cache), 0)

    @mock.patch("inboxen.utils.ratelimit.timezone.now")
    def test_check_does_increase_count_if_full(self, now_mock):
        now_mock.return_value = datetime.utcnow()
        request = MockRequest()
        request.META["REMOTE_ADDR"] = "127.0.0.1"

        for i in range(self.limit_count):
            self.limiter.counter_increase(request)

        self.assertEqual(len(cache._cache), 1)
        self.assertEqual(cache.get(self.make_key(request, now_mock())), self.limit_count)

        self.limiter.counter_full(request)

        self.assertEqual(len(cache._cache), 1)
        self.assertEqual(cache.get(self.make_key(request, now_mock())), self.limit_count + 1)
