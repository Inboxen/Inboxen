##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
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

from django.utils.translation import ugettext as _
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

@login_required
def settings(request):
    error = ""

    # check their html preferences
    profile = request.user.userprofile
    html_pref = profile.flags.prefer_html_email

    # they submitting it?
    if request.method == "POST":
        if "html-preference" in request.POST and request.POST["html-preference"] == "html":
            html_pref = True
        else:
            html_pref = False

        profile.flags.prefer_html_email = html_pref
        profile.save()

        if len(request.POST["username0"]):
            if request.POST["username0"] == request.POST["username1"]:
                request.user.username = request.POST["username0"]
                request.user.save()
            else:
                error = _("Please enter your new username twice.")

    context = {
        "headline":_("Settings"),
        "error": error,
        "htmlpreference": html_pref,
        }

    return render(request, "user/settings/index.html", context)
