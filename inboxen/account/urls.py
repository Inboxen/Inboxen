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

from django import urls
from django.conf import settings as dj_settings
from django.views.generic import TemplateView

from inboxen.account.decorators import anonymous_required
from inboxen.account.views import delete, otp, register, settings, suspended

urlpatterns = [
    urls.re_path(r'^$', settings.GeneralSettingsView.as_view(), name='user-settings'),
    urls.re_path(r'^security/password$', settings.PasswordChangeView.as_view(), name='user-password'),
    urls.re_path(r'^security/sudo/$', settings.InboxenElevateView.as_view(), name='user-sudo'),
    urls.re_path(r'^security/setup/$', otp.setup_view, name='user-twofactor-setup'),
    urls.re_path(r'^security/backup/$', otp.backup_view, name='user-twofactor-backup'),
    urls.re_path(r'^security/backup/download/$', otp.backup_download_view, name='user-twofactor-backup-download'),
    urls.re_path(r'^security/disable/$', otp.disable_view, name='user-twofactor-disable'),
    urls.re_path(r'^security/qrcode/$', otp.qrcode_view, name='user-twofactor-qrcode'),

    urls.re_path(r'^delete/$', delete.AccountDeletionView.as_view(), name='user-delete'),
    urls.re_path(r'^username/$', settings.UsernameChangeView.as_view(), name='user-username'),
    urls.re_path(r'^login/$', otp.login, name='user-login'),
    urls.re_path(r'^logout/$', settings.LogoutView.as_view(), name='user-logout'),

    urls.re_path(r'^returned/$', suspended.returned_user, name='user-returned'),

    # liberation app
    urls.re_path(r'^liberate/', urls.include("inboxen.liberation.urls")),
]

if dj_settings.ENABLE_REGISTRATION:
    urlpatterns += [
        urls.re_path(r'^register/status/$',
                     anonymous_required(TemplateView.as_view(template_name='account/register/software-status.html')),
                     name='user-status'),
        urls.re_path(r'^register/success/$',
                     anonymous_required(TemplateView.as_view(template_name='account/register/success.html')),
                     name='user-success'),
        urls.re_path(r'^register/$',
                     anonymous_required(register.UserRegistrationView.as_view()),
                     name='user-registration'),
    ]
