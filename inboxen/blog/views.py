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

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import gettext as _
from django.views import generic

from inboxen.blog.forms import CreateForm, EditForm
from inboxen.blog.models import BlogPost
from inboxen.cms.decorators import is_secure_admin
from inboxen.cms.forms import DeleteForm


class BlogListView(generic.ListView):
    context_object_name = "posts"
    model = BlogPost
    paginate_by = 5
    template_name = "blog/blog.html"

    def get_queryset(self):
        return super(BlogListView, self).get_queryset().filter(draft=False)


class BlogDetailView(generic.DetailView):
    context_object_name = "post"
    model = BlogPost
    template_name = "blog/post.html"

    def get_queryset(self):
        return super(BlogDetailView, self).get_queryset().filter(draft=False)


class RssFeed(Feed):
    title = "{0} News Feed".format(settings.SITE_NAME)
    feed_url = reverse_lazy('blog-feed-rss')
    link = reverse_lazy('blog')

    def items(self):
        return BlogPost.objects.filter(draft=False).order_by('-date')[:10]

    def item_title(self, item):
        return item.subject

    def item_description(self, item):
        return item.rendered_body

    def item_link(self, item):
        return reverse('blog-post', kwargs={"slug": item.slug})

    def description(self):
        return _("The latest news and updates for {0}").format(settings.SITE_NAME)


class AtomFeed(RssFeed):
    feed_type = Atom1Feed
    subtitle = RssFeed.description
    feed_url = reverse_lazy('blog-feed-atom')


# admin views

@is_secure_admin
def blog_admin_index(request):
    blog_posts = BlogPost.objects.all()

    return TemplateResponse(
        request,
        "blog/admin/index.html",
        {"posts": blog_posts}
    )


@is_secure_admin
def blog_admin_create(request):
    if request.method == "POST":
        form = CreateForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("admin:blog:index"))
    else:
        form = CreateForm(user=request.user)

    return TemplateResponse(
        request,
        "blog/admin/create.html",
        {"form": form},
    )


@is_secure_admin
def blog_admin_edit(request, blog_pk):
    try:
        post = BlogPost.objects.get(pk=blog_pk)
    except BlogPost.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = EditForm(data=request.POST, instance=post)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("admin:blog:index"))
    else:
        form = EditForm(instance=post)

    return TemplateResponse(
        request,
        "blog/admin/edit.html",
        {"form": form, "post": post},
    )


@is_secure_admin
def blog_admin_delete(request, blog_pk):
    try:
        post = BlogPost.objects.get(pk=blog_pk)
    except BlogPost.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = DeleteForm(data=request.POST)
        if form.is_valid():
            post.delete()
            return HttpResponseRedirect(reverse("admin:blog:index"))
    else:
        form = DeleteForm()

    return TemplateResponse(
        request,
        "blog/admin/delete.html",
        {"form": form, "post": post},
    )
