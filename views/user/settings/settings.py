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

    # they submitting it?
    if request.method == "POST":
        if "html-preference" in request.POST:
            if request.POST["html-preference"] == "html":
                profile.flags.prefer_html_email = True
            else:
                profile.flags.prefer_html_email = False

        if "images" in request.POST:
            if request.POST["images"] == "ask":
                profile.flags.ask_images = True
            elif request.POST["images"] == "always":
                profile.flags.display_images = True
                profile.flags.ask_images = False
            elif request.POST["images"] == "never":
                profile.flags.display_images = False
                profile.flags.ask_images = False

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
        "htmlpreference": profile.flags.prefer_html_email,
        "ask_images": profile.flags.ask_images,
        "display_images": profile.flags.display_images,
        }

    return render(request, "user/settings/index.html", context)
