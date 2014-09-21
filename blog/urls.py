##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
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

from django.conf import urls

from blog.views import AtomFeed, RssFeed

# If you're debugging regex, test it out on http://www.debuggex.com/ first - M
urlpatterns = urls.patterns('',
    urls.url(r'^blog/add/', 'blog.views.add', name='blog-post-add'),
    urls.url(r'^blog/post/(?P<postid>\d+)', 'blog.views.post', name='blog-post'),
    urls.url(r'^blog/delete/(?P<postid>\d+)', 'blog.views.delete', name='blog-post-delete'),
    urls.url(r'^blog/edit/(?P<postid>\d+)', 'blog.views.edit', name='blog-post-edit'),
    urls.url(r'^blog/feed/atom', AtomFeed(), name='blog-feed-atom'),
    urls.url(r'^blog/feed/(rss)?', RssFeed(), name='blog-feed-rss'),
    urls.url(r'^blog/(?P<page>\d*)', 'blog.views.view', name='blog'),
    urls.url(r'^$', 'blog.views.view', name='blog'),
    )
