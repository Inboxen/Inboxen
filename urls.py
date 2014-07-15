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

from django.conf import settings, urls
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _

from two_factor.views import core as twofactor

from website import views
from website.forms import PlaceHolderAuthenticationForm, PlaceHolderPasswordChangeForm
from website.views.blog.feed import RssFeed, AtomFeed

# error views
urls.handler500 = 'website.views.error.internal_server'
urls.handler404 = 'website.views.error.not_found'
urls.handler403 = 'website.views.error.permission_denied'

# If you're debugging regex, test it out on http://www.debuggex.com/ first - M
urlpatterns = urls.patterns('',
    urls.url(r'^$', views.Index.as_view(), name='index'),
    urls.url(r'^huh', views.TemplateView.as_view(template_name='huh.html', headline=_('Huh?')), name='huh'),
    
    urls.url(r'^blog/add/', 'website.views.blog.add.add', name='blog-post-add'),
    urls.url(r'^blog/post/(?P<postid>\d+)', 'website.views.blog.view.post', name='blog-post'),
    urls.url(r'^blog/delete/(?P<postid>\d+)', 'website.views.blog.delete.delete', name='blog-post-delete'),
    urls.url(r'^blog/edit/(?P<postid>\d+)', 'website.views.blog.edit.edit', name='blog-post-edit'),
    urls.url(r'^blog/feed/atom', AtomFeed(), name='blog-feed-atom'),
    urls.url(r'^blog/feed/(rss)?', RssFeed(), name='blog-feed-rss'),
    urls.url(r'^blog/(?P<page>\d*)', 'website.views.blog.view.view', name='blog'),
    urls.url(r'^blog/', 'website.views.blog.view.view', name='blog'),

    urls.url(r'^inbox/add/', views.InboxAddView.as_view(), name='inbox-add'),
    urls.url(r'^inbox/edit/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)', views.InboxEditView.as_view(), name='inbox-edit'),
    urls.url(r'^inbox/delete/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)', views.InboxDeletionView.as_view(), name='inbox-delete'),

    urls.url(r'^inbox/attachment/(?P<attachmentid>\d+)/(?P<method>\w+)', views.AttachmentDownloadView.as_view(), name='email-attachment'),
    urls.url(r'^inbox/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)/email/(?P<id>[a-fA-F0-9]+)', views.EmailView.as_view(), name='email-view'),
    urls.url(r'^inbox/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)/(?P<page>\d+)', views.SingleInboxView.as_view(), name='single-inbox'),
    urls.url(r'^inbox/(?P<inbox>[a-zA-Z0-9\.]+)@(?P<domain>[a-zA-Z0-9\.]+)/', views.SingleInboxView.as_view(), name='single-inbox'),
    urls.url(r'^inbox/(?P<page>\d+)', views.UnifiedInboxView.as_view(), name='unified-inbox'),
    urls.url(r'^inbox/', views.UnifiedInboxView.as_view(), name='unified-inbox'),

    urls.url(r'^user/login/', views.LoginView.as_view(), name='user-login'),
    urls.url(r'^user/home/(?P<page>\d+)', views.UserHomeView.as_view(), name='user-home'),
    urls.url(r'^user/home/', views.UserHomeView.as_view(), name='user-home'),
    urls.url(r'^user/search/(?P<q>.*)/(?P<page>\d+)', views.SearchView.as_view(), name='user-search'),
    urls.url(r'^user/search/(?P<q>.*)/', views.SearchView.as_view(), name='user-search'),
    urls.url(r'^user/search/', views.SearchView.as_view(), name='user-search'),


    urls.url(r'^user/settings/security/password', 'django.contrib.auth.views.password_change',
        {
            'template_name': 'user/settings/password.html',
            'post_change_redirect': reverse_lazy('user-twofactor'),
            'password_change_form': PlaceHolderPasswordChangeForm,
            'extra_context': {
                'headline': _('Change Password'),
            },
        },
        name='user-password',
    ),
    urls.url(r'^user/settings/security/setup', views.TwoFactorSetupView.as_view(), name='user-twofactor-setup'),
    urls.url(r'^user/settings/security/disable', views.TwoFactorDisableView.as_view(), name='user-twofactor-disable'),
    urls.url(r'^user/settings/security/qrcode', twofactor.QRGeneratorView.as_view(), name='user-twofactor-qrcode'),
    urls.url(r'^user/settings/security', views.TwoFactorView.as_view(), name='user-twofactor'),

    urls.url(r'^user/settings/liberate/download', views.LiberationDownloadView.as_view(), name='user-liberate-get'),
    urls.url(r'^user/settings/liberate', views.LiberationView.as_view(), name='user-liberate'),
    urls.url(r'^user/settings/delete', views.AccountDeletionView.as_view(), name='user-delete'),
    urls.url(r'^user/settings/', 'website.views.user.settings.settings.settings', name='user-settings'),
    urls.url(r'^user/logout/', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='user-logout'),
)

if settings.ENABLE_REGISTRATION:
    urlpatterns += urls.patterns('',
        urls.url(r'^user/register/status', views.TemplateView.as_view(template_name='user/register/software-status.html', headline=_('We\'re not stable!')), name='user-status'),
        urls.url(r'^user/register/success', views.TemplateView.as_view(template_name='user/register/success.html', headline=_('Welcome!')), name='user-success'),
        urls.url(r'^user/register/', views.UserRegistrationView.as_view(), name='user-registration'),
    )
