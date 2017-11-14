##
#    Copyright (C) 2017 Jessica Tallon & Matt Molyneaux
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

from functools import wraps

from django.conf import settings
from django.core.exceptions import PermissionDenied
from sudo.views import redirect_to_sudo


def is_secure_admin(func):
    """
    Checks that current request is from a superuser, who has 2FA enabled, and
    checks for the sudo cookie
    """
    @wraps(func)
    def inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("Admins must be Superusers")
        elif not (request.user.is_verified() or settings.DEBUG):
            # OTP has a decorator for this, but it bounces the user back to the
            # login page - which will fail because the user is already logged in
            raise PermissionDenied("Admins must have Two Factor Authentication enabled")
        elif not request.is_sudo():
            return redirect_to_sudo(request.get_full_path())

        return func(request, *args, **kwargs)

    # private api to check that decorators have been added
    inner.__dict__.setdefault("_inboxen_decorators", [])
    inner.__dict__["_inboxen_decorators"].append(is_secure_admin)

    return inner
