##
#    Copyright (C) 2013-2014 Jessica Tallon & Matt Molyneaux
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

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext as _

from pytz import utc

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

            return HttpResponseRedirect(reverse('blog'))


    context = {
        "error": error,
        "headline": _("Add Post"),
    }

    return render(request, "blog/add.html", context)

@staff_member_required
def delete(request, postid):

    try:
        post = BlogPost.objects.filter(id=postid).only('id')
    except BlogPost.DoesNotExist:
        return HttpResponseRedirect(reverse('blog'))

    post.delete()

    return HttpResponseRedirect(reverse('blog'))

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
                post.draft = draft

            post.save()

            return HttpResponseRedirect(reverse('blog'))

    context = {
        "error": error,
        "headline": post.subject,
        "post": post,
    }

    return render(request, "blog/edit.html", context)

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
        "headline": _("Blog"),
        "posts": posts,
    }

    return render(request, "blog/blog.html", context)

def post(request, postid):
    if request.user.is_staff:
        kwargs = {"id": postid}
    else:
        kwargs = {"id": postid, "draft": False}

    try:
        p = BlogPost.objects.get(**kwargs)
    except BlogPost.DoesNotExist:
        return HttpResponseRedirect(reverse('blog'))

    context = {
        "headline": p.subject,
        "post": p,
    }

    return render(request, "blog/post.html", context)

class RssFeed(Feed):
    title = "{0} News Feed".format(settings.SITE_NAME)
    feed_url = reverse_lazy('blog-feed-rss')
    link = reverse_lazy('blog')

    def items(self):
        return BlogPost.objects.filter(draft=False).order_by('-date')[:10]

    def item_title(self, item):
        return item.subject

    def item_description(self, item):
        return item.rendered_body()

    def item_link(self, item):
        return reverse('blog-post', kwargs={"postid": item.id})

    def description(self):
        return _("The latest news and updates for {0}").format(settings.SITE_NAME)

class AtomFeed(RssFeed):
    feed_type = Atom1Feed
    subtitle = RssFeed.description
    feed_url = reverse_lazy('blog-feed-atom')
