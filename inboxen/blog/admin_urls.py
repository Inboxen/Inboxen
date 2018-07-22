##
#    Copyright (C) 2017 Jessica Tallon & Matt Molyneaux
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

app_name = "blog"

urlpatterns = [
    urls.url(r'^$', views.blog_admin_index, name='index'),
    urls.url(r'^create/$', views.blog_admin_create, name='create'),
    urls.url(r'^edit/(?P<blog_pk>\d+)/$', views.blog_admin_edit, name='edit'),
    urls.url(r'^delete/(?P<blog_pk>\d+)/$', views.blog_admin_delete, name='delete'),
]
