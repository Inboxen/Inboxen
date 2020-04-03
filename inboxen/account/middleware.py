##
#    Copyright (C) 2020 Jessica Tallon & Matt Molyneaux
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

from django.shortcuts import redirect


class ReturningIcedUser:
    """Displays a message to users who've had their accounts put on ice"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_ajax = request.headers.get("x-requested-with")
        receiving = request.user.inboxenprofile.receiving_emails if hasattr(request.user, "inboxenprofile") else True
        if is_ajax or receiving:
            return self.get_response(request)
        else:
            return redirect("user-returned")
