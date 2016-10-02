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

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from ratelimitbackend.exceptions import RateLimitException
from sudo.views import redirect_to_sudo


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
            request.session.set_expiry(None)
            request.session.modified = True


class SudoAdminMiddleware(object):
    """Protects admin site with Django-Sudo"""
    def process_request(self, request):
        if request.path.startswith(reverse("admin:index")):
            if request.is_sudo():
                return
            else:
                return redirect_to_sudo(request.get_full_path())
