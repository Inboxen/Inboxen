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

from datetime import datetime

from pytz import utc

from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from inboxen.models import BlogPost

@staff_member_required
def add(request):

    error = ""

    if request.method == "POST":
        if not ("title" in request.POST or "body" in request.POST):
            error = _("You need to have a title and the blog's body")
        else:
            if "draft" in request.POST and request.POST["draft"] == "melon":
                draft = True
            else:
                draft = False

            post = BlogPost(
                subject=request.POST["title"],
                body=request.POST["body"],
                date=datetime.now(utc),
                author=request.user,
                modified=datetime.now(utc),
                draft=draft
            )

            post.save()

            return HttpResponseRedirect("/blog/")


    context = {
        "error":error,
        "page":_("Add Post"),
    }

    return render(request, "blog/add.html", context)
