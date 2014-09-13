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
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from inboxen.models import BlogPost

@staff_member_required
def edit(request, postid):

    error = ""

    try:
        post = BlogPost.objects.get(id=postid)
    except BlogPost.DoesNotExist:
        return HttpResponseRedirect(reverse('blog'))

    if request.method == "POST":
        if "draft" in request.POST and request.POST["draft"] == "melon":
            draft = True
        else:
            draft = False

        if not ("subject" in request.POST or "body" in request.POST):
            error = _("You need to specify the subject and body of the post")
        elif draft and not post.draft:
            error = _("You may not unpublish a post - please delete it instead.")
        else:
            post.subject = request.POST["subject"]
            post.body = request.POST["body"]
            post.modified = datetime.now(utc)

            if post.draft and not draft:
                post.date = post.modified
                post.draft=draft

            post.save()

            return HttpResponseRedirect(reverse('blog'))

    context = {
        "error":error,
        "headline":post.subject,
        "post":post,
    }

    return render(request, "blog/edit.html", context)
