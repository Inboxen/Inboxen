##
#    This file is part of front-end.
#
#    front-end is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    front-end is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with front-end.  If not, see <http://www.gnu.org/licenses/>.
##

from django.conf import settings
from django.shortcuts import render

def error(request, error_message, status=500):

    if "user" not in dir(request) or request.user.is_authenticated():
        registration_enabled = False
    elif settings.ENABLE_REGISTRATION:
        registration_enabled = False
    else:
        registration_enabled = True

    context = {
        "page":"Page not found",
        "error":error_message,
        "registration_enabled":registration_enabled,
    }

    return render(request, "error.html", context, status=status)

def not_found(request):
    error_message = """
    The page you have requested has not been found. Please contact support if you believe this page should exist or you're brought to this page due to a link you have clicked while nagivating around the site."""

    return error(request, error_message, status=404)

def internal_server(request):
    error_message = """
    There has been a server problem. We're currently looking into this, please try again soon.
    """

    return error(request, error_message, status=500)

def permission_denied(request):
    error_message = """
    Permission denied, you're not authorized to view this page, sorry.
    """

    return error(request, error_message, status=403)
