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
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from ratelimitbackend.exceptions import RateLimitException
from sudo.views import redirect_to_sudo
from wagtail.wagtailadmin.views.account import login, logout


LOGIN_NAME = "{}.{}".format(login.__module__, login.__name__)
LOGOUT_NAME = "{}.{}".format(logout.__module__, logout.__name__)
SESSION_HALF_COOKIE_AGE = settings.SESSION_COOKIE_AGE / 2


class RateLimitMiddleware(object):
    """Handles exceptions thrown by rate-limited login attepmts."""
    def process_exception(self, request, exception):
        if isinstance(exception, RateLimitException):
            messages.warning(request, _("Too many login attempts, further login attempts will be ignored."))
            return redirect("user-login")


class ExtendSessionMiddleware(object):
    """Extends the expiry of sessions for logged in users"""
    def process_request(self, request):
        if request.user.is_authenticated():
            if '_session_expiry' not in request.session:
                # get_expiry_age() will return settings.SESSION_COOKIE_AGE if
                # "no custom expiry is set". Django devs consider this a
                # feature. We do not.
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                request.session.modified = True
            elif request.session.get_expiry_age() <= SESSION_HALF_COOKIE_AGE:
                # cycle session key
                request.session.cycle_key()
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                request.session.modified = True


class RedirectWagLoginMiddleware(object):
    """Redirects Wagtail's admin login/logout views

    Neither handle 2FA or sudo cookies
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            view_path = "{}.{}".format(view_func.__module__, view_func.__name__)
        except AttributeError:
            view_path = ""

        if view_path == LOGIN_NAME:
            return redirect("user-login")
        elif view_path == LOGOUT_NAME:
            return redirect("user-logout")


class WagtailAdminProtectionMiddleware(object):
    """Protects Wagtail's admin with both sudo and 2FA"""
    def process_request(self, request):
        if request.path.startswith(str(settings.WAGTAIL_ADMIN_BASE_URL)):
            if request.user.is_anonymous():
                # admin has its own redirect for non-logged in users
                return
            elif not request.user.is_verified() and not settings.DEBUG:
                raise PermissionDenied("Admins must have Two Factor Authentication enabled")
            elif not request.is_sudo():
                return redirect_to_sudo(request.get_full_path())
