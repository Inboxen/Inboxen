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
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from inboxen.models import BlogPost

def view(request, page=1):
    if request.user.is_staff:
        posts = BlogPost.objects.all()
    else:
        posts = BlogPost.objects.filter(draft=False)

    posts = posts.order_by("-date")
    paginator = Paginator(posts, 5)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger: # sometimes it's None
        posts = paginator.page(1)
    except EmptyPage: # somestimes the user will try different numbers
        posts = paginator.page(paginator.num_pages)

    context = {
        "page":_("Blog"),
        "posts":posts,
        "settings": settings,
    }

    return render(request, "blog/blog.html", context)

def post(request, postid):
    if request.user.is_staff:
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
        "settings": settings,
    }

    return render(request, "blog/post.html", context)
