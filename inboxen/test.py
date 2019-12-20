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
import warnings

from django import test
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.session import SessionStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse
from django.test.runner import DiscoverRunner
from django.utils.crypto import get_random_string
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.middleware import OTPMiddleware
from django_otp.plugins.otp_static.models import StaticDevice
from elevate import settings as elevate_settings
from elevate.middleware import ElevateMiddleware

_log = logging.getLogger(__name__)


class MockRequest(HttpRequest):
    """Mock up a request object"""

    def __init__(self, user=None, session_id=None, has_otp=False, has_sudo=False):
        super(MockRequest, self).__init__()
        self.method = "GET"

        if user is None:
            self.user = AnonymousUser()
        else:
            self.user = user

        session = SessionMiddleware(lambda x: x)
        self.session = session.SessionStore(session_id)
        self._messages = SessionStorage(self)
        self.META = {"REMOTE_ADDR": "127.0.0.1"}

        # sudo
        ElevateMiddleware(lambda x: x)(self)
        if has_sudo:
            grant_sudo(self)

        # otp
        if has_otp:
            grant_otp(self, self.user)
        OTPMiddleware(lambda x: x)(self)


# TODO: submit to django-elevate?
def grant_sudo(client_or_request):
    """Sets a cookie on the test client or request that django-elevate will use"""
    response = HttpResponse()
    token = get_random_string()

    response.set_signed_cookie(
        elevate_settings.COOKIE_NAME,
        token,
        salt=elevate_settings.COOKIE_SALT,
        max_age=elevate_settings.COOKIE_AGE,
        secure=False,
        httponly=True,
        path=elevate_settings.COOKIE_PATH,
        domain=elevate_settings.COOKIE_DOMAIN,
    )

    if hasattr(client_or_request, "cookies"):
        client_or_request.cookies[elevate_settings.COOKIE_NAME] = response.cookies[elevate_settings.COOKIE_NAME]
    elif hasattr(client_or_request, "COOKIES"):
        client_or_request.COOKIES[elevate_settings.COOKIE_NAME] = response.cookies[elevate_settings.COOKIE_NAME].value
    else:
        raise TypeError("%r has neither cookies nor COOKIES" % client_or_request)

    # client.session is a property that returns new objects
    session = client_or_request.session
    session[elevate_settings.COOKIE_NAME] = token
    session.save()


def grant_otp(client_or_request, user):
    """Sets session data for OTP"""
    device = StaticDevice.objects.get_or_create(user=user)[0]

    # client.session is a property that returns new objects
    session = client_or_request.session
    session[DEVICE_ID_SESSION_KEY] = device.persistent_id
    session.save()


class InboxenTestRunner(DiscoverRunner):
    """Test runner for Inboxen"""
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
