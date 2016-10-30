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
from django.conf.urls.static import static
from django.utils.translation import ugettext as _

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls

from inboxen import admin, views


urls.handler400 = views.error.bad_request
urls.handler403 = views.error.permission_denied
urls.handler404 = views.error.not_found
urls.handler500 = views.error.server_error


# csrf stuff
import session_csrf
session_csrf.monkeypatch()


urlpatterns = [
    urls.url(r'^$', views.Index.as_view(), name='index'),
    urls.url(r'^_csp_report/$', views.error.csp_report, name='csp_logger'),
    urls.url(r'^stats/$', views.stats, name='stats'),
    urls.url(r'^stats_recent.json$', views.stats_recent, name='stats_recent'),

    # inbox views
    urls.url(r'^inbox/add/$', views.InboxAddView.as_view(), name='inbox-add'),
    urls.url(r'^inbox/edit/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)/$', views.InboxEditView.as_view(), name='inbox-edit'),

    urls.url(r'^inbox/attachment/(?P<attachmentid>\d+)/(?P<method>\w+)/$', views.AttachmentDownloadView.as_view(), name='email-attachment'),
    urls.url(r'^inbox/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)/email/(?P<id>[a-fA-F0-9]+)/$', views.EmailView.as_view(), name='email-view'),
    urls.url(r'^inbox/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)/(?P<page>\d+)/$', views.SingleInboxView.as_view(), name='single-inbox'),
    urls.url(r'^inbox/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)/$', views.SingleInboxView.as_view(), name='single-inbox'),
    urls.url(r'^inbox/(?P<page>\d+)/$', views.UnifiedInboxView.as_view(), name='unified-inbox'),
    urls.url(r'^inbox/$', views.UnifiedInboxView.as_view(), name='unified-inbox'),

    # form inlines
    urls.url(r'^forms/inbox/add/$', views.FormInboxAddView.as_view(), name='form-inbox-add'),
    urls.url(r'^forms/home/$', views.FormHomeView.as_view(), name='form-home'),
    urls.url(r'^forms/inbox/edit/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)/$', views.FormInboxEditView.as_view(), name='form-inbox-edit'),
    urls.url(r'^forms/inbox/email/$', views.FormInboxView.as_view(), name='form-inbox-email'),

    # user views
    urls.url(r'^user/home/(?P<page>\d+)/$', views.UserHomeView.as_view(), name='user-home'),
    urls.url(r'^user/home/$', views.UserHomeView.as_view(), name='user-home'),
    urls.url(r'^user/search/(?P<q>.*)/(?P<page>\d+)/$', views.SearchView.as_view(), name='user-search'),
    urls.url(r'^user/search/(?P<q>.*)/$', views.SearchView.as_view(), name='user-search'),
    urls.url(r'^user/search/$', views.SearchView.as_view(), name='user-search'),
    urls.url(r'^user/searchapi/(?P<q>.*)/$', views.SearchApiView.as_view(), name='user-searchapi'),

    # other apps
    urls.url(r'^blog/', urls.include("blog.urls")),
    urls.url(r'^click/', urls.include("redirect.urls")),
    urls.url(r'^source/', urls.include("source.urls")),
    urls.url(r'^user/account/', urls.include("account.urls")),

    # admin
    urls.url(r'^admin/', urls.include(admin.site.urls)),

    # wagtail
    urls.url(r'^cms/', urls.include(wagtailadmin_urls)),
    urls.url(r'^documents/', urls.include(wagtaildocs_urls)),
    urls.url(r'^help/', urls.include(wagtail_urls)),
]

if settings.DEBUG:
    import debug_toolbar  # NOQA

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        urls.url(r'^__debug__/', urls.include(debug_toolbar.urls)),
    ]
