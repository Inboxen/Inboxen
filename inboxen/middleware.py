##
#    Copyright (C) 2014-2016 Jessica Tallon & Matt Molyneaux
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

from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import ugettext as _
from ratelimitbackend.exceptions import RateLimitException

SESSION_HALF_COOKIE_AGE = timedelta(seconds=settings.SESSION_COOKIE_AGE / 2)


class RateLimitMiddleware:
    """Handles exceptions thrown by rate-limited login attepmts."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, RateLimitException):
            messages.warning(request, _("Too many login attempts, further login attempts will be ignored."))
            return redirect("user-login")


class ExtendSessionMiddleware:
    """Extends the expiry of sessions for logged in users"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # this is ugly, but django doesn't make it easy
            session_obj = request.session._get_session_from_db()
            if session_obj is not None:
                cookie_time_left = session_obj.expire_date - timezone.now()
                if cookie_time_left <= SESSION_HALF_COOKIE_AGE:
                    # cycle session key
                    request.session.cycle_key()
                    user_logged_in.send(
                        sender=request.user.__class__,
                        request=request,
                        user=request.user,
                    )
        return self.get_response(request)


class MakeXSSFilterChromeSafeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # we have CSP and filter user input to protect against XSS, adding
        # X-XSS-Protection would be great as a defence in depth. However, there
        # are a few bugs in Chrome that can cause information to be leaked to
        # an attacker. Some of these rely on iframes which we might use in
        # future for sandboxing HTML parts.
        response['x-xss-protection'] = '0'
        return response
