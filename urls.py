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

from website import views
from website.views.blog.feed import RssFeed, AtomFeed



# error views
urls.handler500 = "website.views.error.internal_server"
urls.handler404 = "website.views.error.not_found"
urls.handler403 = "website.views.error.permission_denied"


# If you're debugging regex, test it out on http://www.debuggex.com/ first - M
urlpatterns = urls.patterns('',
    urls.url(r'^$', views.Index.as_view(), name='index'),
    
    urls.url(r'^blog/add/', 'website.views.blog.add.add'),
    urls.url(r'^blog/post/(?P<postid>\d+)', 'website.views.blog.view.post'),
    urls.url(r'^blog/delete/(?P<postid>\d+)', 'website.views.blog.delete.delete'),
    urls.url(r'^blog/edit/(?P<postid>\d+)', 'website.views.blog.edit.edit'),
    urls.url(r'^blog/feed/atom', AtomFeed()),
    urls.url(r'^blog/feed/(rss)?', RssFeed()),
    urls.url(r'^blog(/(?P<page>\d+))?', 'website.views.blog.view.view'),

    urls.url(r'^user/login/', 'django.contrib.auth.views.login', 
        {
            'template_name': 'user/login.html',
            'extra_context': {
                'page':'Login',
                'registration_enabled':settings.ENABLE_REGISTRATION,
            },
        },
    ),
    urls.url(r'^user/register/status', views.TemplateView.as_view(template_name='user/software-status.html', title='We\'re not stable!'), name='user-status'),
    urls.url(r'^user/register/success', views.TemplateView.as_view(template_name='user/register/success.html', title='Welcome!'), name='user-success'),
    urls.url(r'^user/register/', views.UserRegistrationView.as_view(), name='user-registration'),
    urls.url(r'^user/home(/(?P<page>\d+))?', views.UserHomeView.as_view(), name='user-home'),
    urls.url(r'^user/settings/liberate', views.LiberationView.as_view(), name='user-liberate'),
    urls.url(r'^user/settings/password', 'django.contrib.auth.views.password_change',
        {
            'template_name': 'user/settings/password/change.html',
            'post_change_redirect': '/',
            'extra_context': {
                'page': 'Change Password',
            },
        },
    ),
    urls.url(r'^user/settings/delete', views.AccountDeletionView.as_view()),
    urls.url(r'^user/settings/', 'website.views.user.settings.settings.settings'),
    urls.url(r'^user/logout/', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='user-logout'),

    urls.url(r'^email/add/', views.InboxAddView.as_view(), name='email-add'),
    urls.url(r'^email/edit/(?P<inbox>[a-zA-Z0-9\.]+@[a-zA-Z0-9\.]+)', views.EmailEditView.as_view(), name='inbox-edit'),
    urls.url(r'^email/delete/(?P<email>[a-zA-Z0-9\.]+@[a-zA-Z0-9\.]+)', views.EmailDeletionView.as_view(), name='inbox-delete'),

    urls.url(r'^inbox/attachment/(?P<attachmentid>\d+)/(?P<method>\w+)', views.AttachmentDownloadView.as_view(), name='email-attachment-download'),
    urls.url(r'^inbox/(?P<email_address>[a-zA-Z0-9\.]+@[a-zA-Z0-9\.]+)/email/(?P<emailid>[a-fA-F0-9]+)', views.EmailView.as_view(template_name="inbox/email.html"), name='email-view'),
    urls.url(r'^inbox/(?P<email_address>[a-zA-Z0-9\.]+@[a-zA-Z0-9\.]+)(/(?P<page>\d+))?', 'website.views.inbox.inbox.inbox'),

    urls.url(r'^inbox(/(?P<page>\d+))?', 'website.views.inbox.inbox.inbox'),
)
