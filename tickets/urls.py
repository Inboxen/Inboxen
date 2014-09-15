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

import os

from django.conf import settings, urls

from tickets import views

# If you're debugging regex, test it out on http://www.debuggex.com/ first - M
urlpatterns = urls.patterns('',
    urls.url(r'^$', views.QuestionListView.as_view(), name='tickets-index'),
    urls.url(r'^(?P<status>[!]?\w+)/$', views.QuestionListView.as_view(), name='tickets-index'),
    urls.url(r'^(?P<page>)/$', views.QuestionListView.as_view(), name='tickets-index'),
    urls.url(r'^(?P<status>[!]?\w+)/(?P<page>)/$', views.QuestionListView.as_view(), name='tickets-index'),
    urls.url(r'^ticket/(?P<pk>\d+)/$', views.QuestionDetailView.as_view(), name='tickets-detail'),
    )

if ("INBOXEN_ADMIN_ACCESS" in os.environ and os.environ["INBOXEN_ADMIN_ACCESS"]) or settings.DEBUG:
    # Only expose the admin features when we need to
    urlpatterns += urls.patterns('',
        urls.url(r'^admin/$', views.QuestionListAdminView.as_view(), name='tickets-index'),
        urls.url(r'^admin/(?P<status>[!]?\w+)/$', views.QuestionListAdminView.as_view(), name='tickets-index'),
        urls.url(r'^admin/(?P<page>)/$', views.QuestionListAdminView.as_view(), name='tickets-index'),
        urls.url(r'^admin/(?P<status>[!]?\w+)/(?P<page>)/$', views.QuestionListAdminView.as_view(), name='tickets-index'),
        urls.url(r'^admin/ticket/(?P<pk>\d+)/$', views.QuestionDetailAdminView.as_view(), name='tickets-detail'),
        )
