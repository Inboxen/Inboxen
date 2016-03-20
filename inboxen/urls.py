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

import os

from django.conf import settings, urls
from django.contrib import admin
from django.utils.translation import ugettext as _

from inboxen import views

urls.handler400 = views.error.bad_request
urls.handler403 = views.error.permission_denied
urls.handler404 = views.error.not_found
urls.handler500 = views.error.server_error

# csrf stuff
import session_csrf
session_csrf.monkeypatch()


urlpatterns = [
    urls.url(r'^$', views.Index.as_view(), name='index'),
    urls.url(r'^_csp_report/', views.error.csp_report, name='csp_logger'),
    urls.url(r'^stats', views.StatsView.as_view(), name='stats'),

    # inbox views
    urls.url(r'^inbox/add/', views.InboxAddView.as_view(), name='inbox-add'),
    urls.url(r'^inbox/edit/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)', views.InboxEditView.as_view(), name='inbox-edit'),

    urls.url(r'^inbox/attachment/(?P<attachmentid>\d+)/(?P<method>\w+)', views.AttachmentDownloadView.as_view(), name='email-attachment'),
    urls.url(r'^inbox/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)/email/(?P<id>[a-fA-F0-9]+)', views.EmailView.as_view(), name='email-view'),
    urls.url(r'^inbox/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)/(?P<page>\d+)', views.SingleInboxView.as_view(), name='single-inbox'),
    urls.url(r'^inbox/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)/', views.SingleInboxView.as_view(), name='single-inbox'),
    urls.url(r'^inbox/(?P<page>\d+)', views.UnifiedInboxView.as_view(), name='unified-inbox'),
    urls.url(r'^inbox/', views.UnifiedInboxView.as_view(), name='unified-inbox'),

    # form inlines
    urls.url(r'^forms/inbox/edit/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)/', views.FormInboxEditView.as_view(), name='form-inbox-edit'),
    urls.url(r'^forms/inbox/email/', views.FormInboxView.as_view(), name='form-inbox-email'),

    # user views
    urls.url(r'^user/home/(?P<page>\d+)', views.UserHomeView.as_view(), name='user-home'),
    urls.url(r'^user/home/', views.UserHomeView.as_view(), name='user-home'),
    urls.url(r'^user/search/(?P<q>.*)/(?P<page>\d+)', views.SearchView.as_view(), name='user-search'),
    urls.url(r'^user/search/(?P<q>.*)/', views.SearchView.as_view(), name='user-search'),
    urls.url(r'^user/search/', views.SearchView.as_view(), name='user-search'),
    urls.url(r'^user/searchapi/(?P<q>.*)/', views.SearchApiView.as_view(), name='user-searchapi'),


    # other apps
    urls.url(r'^blog/', urls.include("blog.urls")),
    urls.url(r'^click/', urls.include("redirect.urls")),
    urls.url(r'^help/', urls.include("termsofservice.urls")),
    urls.url(r'^help/tickets/', urls.include("tickets.urls")),
    urls.url(r'^source/', urls.include("source.urls")),
    urls.url(r'^user/account/', urls.include("account.urls")),
]

if ("INBOXEN_ADMIN_ACCESS" in os.environ and os.environ["INBOXEN_ADMIN_ACCESS"]) or settings.DEBUG:
    admin.autodiscover()

    urlpatterns += [
        urls.url(r'^admin/', urls.include(admin.site.urls)),
    ]
