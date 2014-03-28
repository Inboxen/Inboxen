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
    if profile.flags.prefer_html_email:
        html_pref = 2
    else:
        html_pref = 1

    # they submitting it?
    if request.method == "POST":

        html_pref = int(request.POST["html-preference"])
        if html_pref == 2:
            profile.flags.prefer_html_email = True
        else:
            profile.flags.prefer_html_email = False
        profile.save()

        if len(request.POST["username0"]):
            if request.POST["username0"] == request.POST["username1"]:
                request.user.username = request.POST["username0"]
                request.user.save()
            else:
                error = _("Please enter your new username twice.")

    context = {
        "page":_("Settings"),
        "error": error,
        "htmlpreference": html_pref,
        }

    return render(request, "user/settings/index.html", context)
