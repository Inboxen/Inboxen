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

from django import urls

from inboxen.tickets import views

urlpatterns = [
    urls.re_path(
        r'^$',
        views.QuestionHomeView.as_view(),
        name='tickets-index'
    ),
    urls.re_path(
        r'^status/(?P<status>[!]?\w+)/$',
        views.QuestionListView.as_view(),
        name='tickets-list'
    ),
    urls.re_path(
        r'^status/(?P<status>[!]?\w+)/(?P<page>\d+)/$',
        views.QuestionListView.as_view(),
        name='tickets-list'
    ),
    urls.re_path(
        r'^ticket/(?P<pk>\d+)/$',
        views.QuestionDetailView.as_view(),
        name='tickets-detail'
    ),
]
