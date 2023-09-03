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

from django import urls

from inboxen.cms import views

urlpatterns = [
    urls.re_path(r'^$', views.index, name='index'),
    urls.re_path(r'^(?P<page_pk>\d+)/$', views.index, name='index'),
    urls.re_path(r'^choose_new_page/(?P<parent_pk>\d+)/$', views.choose_page_type, name='choose-page-type'),
    urls.re_path(r'^create_page/(?P<model>[A-Za-z]+)/(?P<parent_pk>\d+)/$', views.create_page, name='create-page'),
    urls.re_path(r'^edit_page/(?P<page_pk>\d+)/$', views.edit_page, name='edit-page'),
    urls.re_path(r'^delete_page/(?P<page_pk>\d+)/$', views.delete_page, name='delete-page'),

    urls.re_path(r'^blog/', urls.include(("inboxen.blog.admin_urls", "blog"), namespace="blog")),
    urls.re_path(r'^questions/', urls.include(("inboxen.tickets.admin_urls", "tickets"), namespace="tickets")),
    urls.re_path(r'^domains/', urls.include(("inboxen.admin_urls.domains", "inboxen"), namespace="domains")),
]
