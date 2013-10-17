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

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *

from website.views.blog.feed import RssFeed, AtomFeed


# error views
handler500 = "website.views.error.internal_server"
handler404 = "website.views.error.not_found"
handler403 = "website.views.error.permission_denied"


# If you're debugging regex, test it out on http://www.debuggex.com/ first - M
urlpatterns = patterns('',
    url(r'^$', 'website.views.index.index'),
    
    url(r'^blog/add/', 'website.views.blog.add.add'),
    url(r'^blog/post/(?P<postid>\d+)', 'website.views.blog.view.post'),
    url(r'^blog/delete/(?P<postid>\d+)', 'website.views.blog.delete.delete'),
    url(r'^blog/edit/(?P<postid>\d+)', 'website.views.blog.edit.edit'),
    url(r'^blog/feed/atom', AtomFeed()),
    url(r'^blog/feed/(rss)?', RssFeed()),
    url(r'^blog(/(?P<page>\d+))?', 'website.views.blog.view.view'),

    url(r'^help/contact/success', 'website.views.help.contact.success.success'),
    url(r'^help/contact/reply', 'website.views.help.contact.reply.reply'),
    url(r'^help/contact/', 'website.views.help.contact.contact'),

    url(r'^user/deleted/', 'website.views.user.settings.delete.success'),
    url(r'^user/login/', 'django.contrib.auth.views.login', 
        {
            'template_name': 'user/login.html',
            'extra_context': {
                'page':'Login',
                'registration_enabled':settings.ENABLE_REGISTRATION,
            },
        },
    ),
    url(r'^user/register/status', 'website.views.user.register.status'),
    url(r'^user/register/success', 'website.views.user.register.success'),
    url(r'^user/register/', 'website.views.user.register.register'),
    url(r'^user/home(/(?P<page>\d+))?', 'website.views.user.home.home'),
    url(r'^user/settings/liberate', 'website.views.user.settings.liberate.liberate.liberate'),
    url(r'^user/settings/password', 'django.contrib.auth.views.password_change',
        {
            'template_name':'user/settings/password/change.html',
            'post_change_redirect':'/',
            'extra_context':{
                'page':'Change Password',
            },
        },
    ),
    url(r'^user/settings/delete', 'website.views.user.settings.delete.delete'),
    url(r'^user/settings/', 'website.views.user.settings.settings.settings'),
    url(r'^user/logout/', 'website.views.user.logout.logout'),

    url(r'^email/add/', 'website.views.email.add.add'),
    url(r'^email/edit/(?P<email>[a-zA-Z0-9\.]+@[a-zA-Z0-9\.]+)', 'website.views.email.edit.edit'),
    url(r'^email/delete/(?P<email>[a-zA-Z0-9\.]+@[a-zA-Z0-9\.]+)', 'website.views.email.delete.confirm'),

    url(r'^inbox/attachment/(?P<attachmentid>\d+)/(?P<method>\w+)', 'website.views.inbox.attachment.download'),
    url(r'^inbox/(?P<email_address>[a-zA-Z0-9\.]+@[a-zA-Z0-9\.]+)/delete/(?P<emailid>[a-fA-F0-9]+)', 'website.views.inbox.delete.delete'),
    url(r'^inbox/(?P<email_address>[a-zA-Z0-9\.]+@[a-zA-Z0-9\.]+)/view/(?P<emailid>[a-fA-F0-9]+)', 'website.views.inbox.view.view'),
    url(r'^inbox/(?P<email_address>[a-zA-Z0-9\.]+@[a-zA-Z0-9\.]+)(/(?P<page>\d+))?', 'website.views.inbox.inbox.inbox'),

    url(r'^inbox(/(?P<page>\d+))?', 'website.views.inbox.inbox.inbox'),

    url(r'^admin/support(/(?P<page>\d+))?', 'website.views.admin.support.support'),
    url(r'^admin/requests', 'website.views.admin.requests.requests'),
    url(r'^admin/', "website.views.admin.index.index"),
)
