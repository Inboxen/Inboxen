##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
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

from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.session import SessionStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse

from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.middleware import OTPMiddleware
from django_otp.plugins.otp_static.models import StaticDevice
from sudo import settings as sudo_settings
from sudo.middleware import SudoMiddleware
from sudo.utils import get_random_string


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
