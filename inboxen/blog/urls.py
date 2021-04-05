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

from inboxen.blog import views

urlpatterns = [
    urls.re_path(r'^post/(?P<slug>[-\w]+)/$', views.BlogDetailView.as_view(), name='blog-post'),
    urls.re_path(r'^feed/atom/$', views.AtomFeed(), name='blog-feed-atom'),
    urls.re_path(r'^feed/(rss/)?$', views.RssFeed(), name='blog-feed-rss'),
    urls.re_path(r'^(?P<page>\d*)/$', views.BlogListView.as_view(), name='blog'),
    urls.re_path(r'^$', views.BlogListView.as_view(), name='blog'),
]
