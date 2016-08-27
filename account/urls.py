##
#    Copyright (C) 2014, 2016 Jessica Tallon & Matt Molyneaux
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

from django.conf import settings as dj_settings, urls
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from two_factor.views import core as twofactor

from account.decorators import anonymous_required
from account.forms import PlaceHolderPasswordChangeForm
from account.views import delete, otp, register, settings


urlpatterns = [
    urls.url(r'^$', settings.GeneralSettingsView.as_view(), name='user-settings'),
    urls.url(r'^security/password$', auth_views.password_change,
        {
            'template_name': 'account/password.html',
            'post_change_redirect': reverse_lazy('user-security'),
            'password_change_form': PlaceHolderPasswordChangeForm,
        },
        name='user-password',
    ),
    urls.url(r'^security/setup/$', otp.setup_view, name='user-twofactor-setup'),
    urls.url(r'^security/backup/$', otp.backup_view, name='user-twofactor-backup'),
    urls.url(r'^security/disable/$', otp.disable_view, name='user-twofactor-disable'),
    urls.url(r'^security/qrcode/$', otp.qrcode_view, name='user-twofactor-qrcode'),
    urls.url(r'^security/$', otp.twofactor_view, name='user-security'),

    urls.url(r'^delete/$', delete.AccountDeletionView.as_view(), name='user-delete'),
    urls.url(r'^username/$', settings.UsernameChangeView.as_view(), name='user-username'),
    urls.url(r'^login/$', otp.login, name='user-login'),
    urls.url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='user-logout'),

    # liberation app
    urls.url(r'^liberate/', urls.include("liberation.urls")),
]

if dj_settings.ENABLE_REGISTRATION:
    urlpatterns += [
        urls.url(r'^register/status/$', anonymous_required(TemplateView.as_view(template_name='account/register/software-status.html')), name='user-status'),
        urls.url(r'^register/success/$', anonymous_required(TemplateView.as_view(template_name='account/register/success.html')), name='user-success'),
        urls.url(r'^register/$', anonymous_required(register.UserRegistrationView.as_view()), name='user-registration'),
    ]
