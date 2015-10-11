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

from django.conf import settings as dj_settings, urls
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _

from two_factor.views import core as twofactor

from account.forms import PlaceHolderPasswordChangeForm
from account.views import delete, login, otp, register, settings
from website import views


# If you're debugging regex, test it out on http://www.debuggex.com/ first - M
urlpatterns = urls.patterns('',
    urls.url(r'^$', settings.GeneralSettingsView.as_view(), name='user-settings'),
    urls.url(r'^security/password', 'django.contrib.auth.views.password_change',
        {
            'template_name': 'user/account/password.html',
            'post_change_redirect': reverse_lazy('user-security'),
            'password_change_form': PlaceHolderPasswordChangeForm,
            'extra_context': {
                'headline': _('Change Password'),
            },
        },
        name='user-password',
    ),
    urls.url(r'^security/setup', otp.TwoFactorSetupView.as_view(), name='user-twofactor-setup'),
    urls.url(r'^security/backup', otp.TwoFactorBackupView.as_view(), name='user-twofactor-backup'),
    urls.url(r'^security/disable', otp.TwoFactorDisableView.as_view(), name='user-twofactor-disable'),
    urls.url(r'^security/qrcode', twofactor.QRGeneratorView.as_view(), name='user-twofactor-qrcode'),
    urls.url(r'^security', otp.TwoFactorView.as_view(), name='user-security'),

    urls.url(r'^delete', delete.AccountDeletionView.as_view(), name='user-delete'),
    urls.url(r'^username', settings.UsernameChangeView.as_view(), name='user-username'),
    urls.url(r'^login/', login.LoginView.as_view(), name='user-login'),
    urls.url(r'^logout/', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='user-logout'),

    # liberation app
    urls.url(r'^liberate/', urls.include("liberation.urls")),
)

if dj_settings.ENABLE_REGISTRATION:
    urlpatterns += urls.patterns('',
        urls.url(r'^register/status', views.TemplateView.as_view(template_name='account/register/software-status.html', headline=_('We\'re not stable!')), name='user-status'),
        urls.url(r'^register/success', views.TemplateView.as_view(template_name='account/register/success.html', headline=_('Welcome!')), name='user-success'),
        urls.url(r'^register/', register.UserRegistrationView.as_view(), name='user-registration'),
    )
