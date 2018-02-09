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

import logging
import os
import sys
import warnings

from django import test
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.session import SessionStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse
from django_assets import env as assets_env
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.middleware import OTPMiddleware
from django_otp.plugins.otp_static.models import StaticDevice
from djcelery.contrib.test_runner import CeleryTestSuiteRunner
from sudo import settings as sudo_settings
from sudo.middleware import SudoMiddleware
from sudo.utils import get_random_string
import six


_log = logging.getLogger(__name__)


class MockRequest(HttpRequest):
    """Mock up a request object"""

    def __init__(self, user=None, session_id="12345678", has_otp=False, has_sudo=False):
        super(MockRequest, self).__init__()
        self.method = "GET"

        if user is None:
            self.user = AnonymousUser()
        else:
            self.user = user

        session = SessionMiddleware()
        self.session = session.SessionStore(session_id)
        self._messages = SessionStorage(self)
        self.META = {"REMOTE_ADDR": "127.0.0.1"}

        # sudo
        SudoMiddleware().process_request(self)
        if has_sudo:
            grant_sudo(self)

        # otp
        if has_otp:
            grant_otp(self, self.user)
        OTPMiddleware().process_request(self)


# TODO: submit to django-sudo?
def grant_sudo(client_or_request):
    """Sets a cookie on the test client or request that django-sudo will use"""
    response = HttpResponse()
    token = get_random_string()

    response.set_signed_cookie(
        sudo_settings.COOKIE_NAME, token,
                salt=sudo_settings.COOKIE_SALT,
                max_age=sudo_settings.COOKIE_AGE,
                secure=False,
                httponly=True,
                path=sudo_settings.COOKIE_PATH,
                domain=sudo_settings.COOKIE_DOMAIN,
    )

    if hasattr(client_or_request, "cookies"):
        client_or_request.cookies[sudo_settings.COOKIE_NAME] = response.cookies[sudo_settings.COOKIE_NAME]
    elif hasattr(client_or_request, "COOKIES"):
        client_or_request.COOKIES[sudo_settings.COOKIE_NAME] = response.cookies[sudo_settings.COOKIE_NAME].value
    else:
        raise TypeError("%r has neither cookies nor COOKIES" % client_or_request)

    # client.session is a property that returns new objects
    session = client_or_request.session
    session[sudo_settings.COOKIE_NAME] = token
    session.save()


def grant_otp(client_or_request, user):
    """Sets session data for OTP"""
    device = StaticDevice.objects.get_or_create(user=user)[0]

    # client.session is a property that returns new objects
    session = client_or_request.session
    session[DEVICE_ID_SESSION_KEY] = device.persistent_id
    session.save()


class WebAssetsOverrideMixin(object):
    """Reset Django Assets crap

    Work around for https://github.com/miracle2k/django-assets/issues/44
    """

    asset_modules = ["inboxen.assets"]

    def disable(self, *args, **kwargs):
        ret_value = super(WebAssetsOverrideMixin, self).disable(*args, **kwargs)

        # reset asset env
        assets_env.reset()
        assets_env._ASSETS_LOADED = False

        # unload asset modules so python reimports them
        for module in self.asset_modules:
            try:
                del sys.modules[module]
                __import__(module)
            except (KeyError, ImportError):
                _log.debug("Couldn't find %s in sys.modules", module)

        return ret_value


class override_settings(WebAssetsOverrideMixin, test.utils.override_settings):
    pass


class InboxenTestRunner(CeleryTestSuiteRunner):
    """Test runner for Inboxen

    Build on top of djcelery's test runner
    """
    def setup_test_environment(self, **kwargs):
        self.is_testing_var_set = int(os.getenv('INBOXEN_TESTING', '0')) > 0
        super(InboxenTestRunner, self).setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs):
        super(InboxenTestRunner, self).teardown_test_environment(**kwargs)
        if not self.is_testing_var_set:
            warnings.warn("You did not set 'INBOXEN_TESTING' in your environment. Test results will be unreliable!")


CLIENT_METHODS_TO_MAKE_SECURE = [
    'get',
    'post',
    'head',
    'trace',
    'options',
    'put',
    'patch',
    'delete',
]


class SecureClient(test.Client):
    """Like Client, but changes the deafult "secure" kwargs to True on certain methods"""
    def __getattribute__(self, name):
        attr = super(SecureClient, self).__getattribute__(name)
        if name in CLIENT_METHODS_TO_MAKE_SECURE:

            def be_secure(*args, **kwargs):
                kwargs.setdefault("secure", True)
                return attr(*args, **kwargs)

            return be_secure
        else:
            return attr


class InboxenTestCase(test.TestCase):
    client_class = SecureClient

    def assertCountEqual(self, actual, expected, msg=None):
        if six.PY3:
            return super(InboxenTestCase, self).assertCountEqual(actual, expected, msg)
        else:
            return self.assertItemsEqual(actual, expected, msg)
