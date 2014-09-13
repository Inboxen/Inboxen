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
    template_name = "user/account/security.html"
    headline = _("Two Factor Authenication")

class TwoFactorBackupView(base.CommonContextMixin, core.BackupTokensView):
    template_name = "user/account/twofactor-backup.html"
    headline = _("Backup Tokens")
    redirect_url = "user-security"

class TwoFactorDisableView(base.CommonContextMixin, profile.DisableView):
    template_name = "user/account/twofactor-disable.html"
    headline = _("Disable Two Factor Authentication")
    redirect_url = "user-security"

class TwoFactorSetupView(base.CommonContextMixin, core.SetupView):
    template_name = "user/account/twofactor-setup.html"
    headline = _("Setup Two Factor Authentication")
    form_list = (
        ('welcome', forms.Form),
        ('method', inboxen_forms.MethodForm),
        ('generator', two_forms.TOTPDeviceForm),
        )
    redirect_url = "user-security"
    qrcode_url = "user-twofactor-qrcode"

    def done(self, *args, **kwargs):
        out = super(TwoFactorSetupView, self).done(*args, **kwargs)
        messages.success(self.request, _("Two factor authentication has been enabled on your account."))

        return out

    def get(self, request, *args, **kwargs):
        """A special GET request won't reset the wizard"""
        if "qr" in request.GET:
            return self.render(self.get_form())
        else:
            return super(TwoFactorSetupView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(TwoFactorSetupView, self).get_context_data(*args, **kwargs)
        if self.steps.current == 'generator':
            context["secret"] = self.request.session[self.session_key_name]
            context["qr"] = int(self.request.GET.get("qr", "1"))

        return context
