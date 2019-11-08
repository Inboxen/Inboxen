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

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import ugettext as _
from ratelimitbackend.exceptions import RateLimitException

SESSION_HALF_COOKIE_AGE = settings.SESSION_COOKIE_AGE / 2


class RateLimitMiddleware(MiddlewareMixin):
    """Handles exceptions thrown by rate-limited login attepmts."""
    def process_exception(self, request, exception):
        if isinstance(exception, RateLimitException):
            messages.warning(request, _("Too many login attempts, further login attempts will be ignored."))
            return redirect("user-login")


class ExtendSessionMiddleware(MiddlewareMixin):
    """Extends the expiry of sessions for logged in users"""
    def process_request(self, request):
        if request.user.is_authenticated:
            if '_session_expiry' not in request.session:
                # get_expiry_age() will return settings.SESSION_COOKIE_AGE if
                # no custom expiry is set.
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                request.session.modified = True
            elif request.session.get_expiry_age() <= SESSION_HALF_COOKIE_AGE:
                # cycle session key
                request.session.cycle_key()
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                request.session.modified = True
                user_logged_in.send(
                    sender=request.user.__class__,
                    request=request,
                    user=request.user,
                )


class MakeXSSFilterChromeSafeMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # we have CSP and filter user input to protect against XSS, adding
        # X-XSS-Protection would be great as a defence in depth. However, there
        # are a few bugs in Chrome that can cause information to be leaked to
        # an attacker. Some of these rely on iframes which we might use in
        # future for sandboxing HTML parts.
        response['x-xss-protection'] = '0'
        return response
