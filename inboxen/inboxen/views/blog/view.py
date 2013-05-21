##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
#   
#    This file is part of Inboxen front-end.
#
#    Inboxen front-end is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen front-end is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen front-end.  If not, see <http://www.gnu.org/licenses/>.
##
from django.conf import settings

from inboxen.models import BlogPost

from django.shortcuts import render
from django.http import HttpResponseRedirect


def view(request):
    if request.user.is_staff:
        posts = BlogPost.objects.all()
    else:
        posts = BlogPost.objects.filter(draft=False)

    posts = posts.order_by("-date")

    context = {
        "page":"Blog",
        "posts":posts,
        "registration_enabled":settings.ENABLE_REGISTRATION,
    }

    return render(request, "blog/blog.html", context)

def post(request, postid):
    if request.user.is_stuff:
        kwargs = {"id": postid}
    else:
        kwargs = {"id": postid, "draft":False}

    try:
        p = BlogPost.objects.get(**kwargs)
    except BlogPost.DoesNotExist:
        return HttpResponseRedirect("/blog/")

    context = {
        "page":p.subject,
        "post":p,
        "registration_enabled":settings.ENABLE_REGISTRATION,
    }

    return render(request, "blog/post.html", context)
