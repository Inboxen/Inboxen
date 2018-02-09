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

from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError, SuspiciousOperation
from django.utils.translation import ugettext as _
from sudo.decorators import sudo_required
from two_factor import forms as two_forms
from two_factor.views import core, profile

from account.forms import PlaceHolderAuthenticationForm
from account.decorators import anonymous_required


class LoginView(core.LoginView):
    template_name = "account/login.html"
    form_list = (
        ('auth', PlaceHolderAuthenticationForm),
        ('token', two_forms.AuthenticationTokenForm),
        ('backup', two_forms.BackupTokenForm),
    )

    def get_form_kwargs(self, step):
        if step == "auth":
            return {"request": self.request}
        else:
            return super(LoginView, self).get_form_kwargs(step)

    def post(self, *args, **kwargs):
        try:
            return super(LoginView, self).post(*args, **kwargs)
        except ValidationError:
            raise SuspiciousOperation("ManagementForm data is missing or has been tampered.")


class TwoFactorSetupView(core.SetupView):
    template_name = "account/twofactor-setup.html"
    form_list = (
        ('welcome', forms.Form),
        ('method', two_forms.MethodForm),
        ('generator', two_forms.TOTPDeviceForm),
    )
    success_url = "user-twofactor-backup"
    qrcode_url = "user-twofactor-qrcode"

    def done(self, *args, **kwargs):
        out = super(TwoFactorSetupView, self).done(*args, **kwargs)
        messages.success(self.request, _("Two factor authentication has been enabled on your account."))

        return out

    def get_context_data(self, **kwargs):
        context = super(TwoFactorSetupView, self).get_context_data(**kwargs)
        if self.steps.current == 'generator':
            context["secret"] = self.request.session[self.session_key_name]

        return context

    def post(self, *args, **kwargs):
        try:
            return super(TwoFactorSetupView, self).post(*args, **kwargs)
        except ValidationError:
            raise SuspiciousOperation("ManagementForm data is missing or has been tampered.")


backup_view = sudo_required(core.BackupTokensView.as_view(template_name="account/twofactor-backup.html", success_url="user-twofactor-backup"))
disable_view = sudo_required(profile.DisableView.as_view(template_name="account/twofactor-disable.html", success_url="user-security"))
login = anonymous_required(LoginView.as_view())
setup_view = sudo_required(TwoFactorSetupView.as_view())
qrcode_view = sudo_required(core.QRGeneratorView.as_view())
twofactor_view = profile.ProfileView.as_view(template_name="account/security.html")
