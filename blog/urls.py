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

from blog import views


urlpatterns = [
    urls.url(r'^post/(?P<slug>[-\w]+)', views.BlogDetailView.as_view(), name='blog-post'),
    urls.url(r'^feed/atom', views.AtomFeed(), name='blog-feed-atom'),
    urls.url(r'^feed/(rss)?', views.RssFeed(), name='blog-feed-rss'),
    urls.url(r'^(?P<page>\d*)', views.BlogListView.as_view(), name='blog'),
    urls.url(r'^$', views.BlogListView.as_view(), name='blog'),
]
