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

from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse
from django.contrib.messages.storage.session import SessionStorage

from sudo.utils import get_random_string
from sudo import settings as sudo_settings


class MockRequest(HttpRequest):
    """Mock up a request object"""

    def __init__(self, user, session_id="12345678"):
        super(MockRequest, self).__init__()
        self.user = user
        session = SessionMiddleware()
        self.session = session.SessionStore(session_id)
        self._messages = SessionStorage(self)
        self.META = {"REMOTE_ADDR": "127.0.0.1"}


# TODO: submit to django-sudo?
def grant_client_sudo(client):
    """Sets a cookie on the test client that django-sudo will use"""
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
    client.cookies[sudo_settings.COOKIE_NAME] = response.cookies[sudo_settings.COOKIE_NAME]
    session = client.session
    session[sudo_settings.COOKIE_NAME] = token
    session.save()
