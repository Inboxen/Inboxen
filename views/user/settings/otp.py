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

from django import http, forms
from django.contrib import messages
from django.core import urlresolvers
from django.utils.translation import ugettext as _

from two_factor import forms as two_forms
from two_factor.views import core, profile

from website import forms as inboxen_forms
from website.views import base

__all__ = ["TwoFactorView", "TwoFactorBackupView", "TwoFactorDisableView", "TwoFactorSetupView"]

class TwoFactorView(base.CommonContextMixin, profile.ProfileView):
    template_name = "user/settings/twofactor.html"
    headline = _("Two Factor Authenication")

class TwoFactorBackupView(base.CommonContextMixin, core.BackupTokensView):
    template_name = "user/settings/twofactor-backup.html"
    headline = _("Backup Tokens")
    redirect_url = "user-twofactor"

class TwoFactorDisableView(base.CommonContextMixin, profile.DisableView):
    template_name = "user/settings/twofactor-disable.html"
    headline = _("Disable Two Factor Authentication")
    redirect_url = "user-twofactor"

class TwoFactorSetupView(base.CommonContextMixin, core.SetupView):
    template_name = "user/settings/twofactor-setup.html"
    headline = _("Setup Two Factor Authentication")
    form_list = (
        ('welcome', forms.Form),
        ('method', inboxen_forms.MethodForm),
        ('generator', two_forms.TOTPDeviceForm),
        )
    redirect_url = "user-twofactor"
    qrcode_url = "user-twofactor-qrcode"

    def done(self, *args, **kwargs):
        messages.success(self.request, _("Two factor authentication has been enabled on your account."))
