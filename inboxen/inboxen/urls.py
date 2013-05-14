##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
#   
#    This file is part of Inboxen front-end.
#
#    Inboxen front-end is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen front-end is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen front-end.  If not, see <http://www.gnu.org/licenses/>.
##

from django.conf import settings
from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^$', 'inboxen.views.index.index'),
    
    url(r'^help/contact/', 'inboxen.views.help.contact.contact'),

    url(r'^user/login/', 'django.contrib.auth.views.login', 
        {
            'template_name': 'user/login.html',
            'extra_context': {
                'page':'Login',
                'registration_enabled':settings.ENABLE_REGISTRATION,
            },
        },
    ),
    url(r'^user/register/', 'inboxen.views.user.register.register'),
    url(r'^user/profile/(?P<page>\d+)', 'inboxen.views.user.profile.profile'),
    url(r'^user/profile/', 'inboxen.views.user.profile.profile'),
    url(r'^user/settings/password', 'django.contrib.auth.views.password_change',
        {
            'template_name':'user/settings/password/change.html',
            'post_change_redirect':'/',
            'extra_context':{
                'page':'Change Password',
            },
        },
    ),
    url(r'^user/settings/', 'inboxen.views.user.settings.settings'),
    url(r'^user/logout/', 'inboxen.views.user.logout.logout'),

    url(r'^email/add/', 'inboxen.views.email.add.add'),
    url(r'^email/request/', 'inboxen.views.email.request.request'),
    url(r'^email/edit/(?P<email>[a-zA-Z0-9@\.]+)', 'inboxen.views.email.edit.edit'),
    url(r'^email/delete/(?P<email>[a-zA-Z0-9@\.]+)', 'inboxen.views.email.delete.confirm'),

    url(r'^inbox/(?P<email_address>[a-zA-Z0-9@\.]+)/view/(?P<emailid>\d+)', 'inboxen.views.inbox.view.view'),
    url(r'^inbox/(?P<email_address>[a-zA-Z0-9@\.]+)(/(?P<page>\d+))?', 'inboxen.views.inbox.inbox.inbox'),
    url(r'^inbox/attachment/(?P<attachment_id>\d+)/(?P<method>\w+)/', 'inboxen.views.inbox.attachment.download'),

    url(r'^inbox/', 'inboxen.views.inbox.inbox.inbox'),

    url(r'^admin/', "inboxen.views.admin.index.index"),
)
