##
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

from django.utils.translation import ugettext as _
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
        "page":_("Page not found"),
        "error":error_message,
        "registration_enabled":registration_enabled,
    }

    return render(request, "error.html", context, status=status)

def not_found(request):
    error_message = _("""
    The page you have requested has not been found.""")

    return error(request, error_message, status=404)

def internal_server(request):
    error_message = _("""
    There has been a server problem. We're currently looking into this, please try again later.
    """)

    return error(request, error_message, status=500)

def permission_denied(request):
    error_message = _("""
    Permission denied, you're not authorized to view this page.
    """)

    return error(request, error_message, status=403)
