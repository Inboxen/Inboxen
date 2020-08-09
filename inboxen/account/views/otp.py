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
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django_otp.decorators import otp_required
from elevate.decorators import elevate_required
from two_factor import forms as two_forms
from two_factor.views import core, profile

from inboxen.account.decorators import anonymous_required
from inboxen.account.forms import PlaceHolderAuthenticationForm


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


@never_cache
@otp_required
@elevate_required
def backup_download_view(request):
    static_device = request.user.staticdevice_set.get_or_create(name='backup')[0]
    if static_device.token_set.count() == 0:
        raise Http404

    response = TemplateResponse(request, "account/twofactor-backup-download.txt",
                                context={"tokens": static_device.token_set.all()},
                                content_type="text/plain")
    response["Content-Disposition"] = "attachment; filename=\"inboxen-backup-tokens.txt\""

    return response


backup_view = elevate_required(core.BackupTokensView.as_view(template_name="account/twofactor-backup.html",
                                                             success_url="user-twofactor-backup"))
disable_view = elevate_required(otp_required(profile.DisableView.as_view(template_name="account/twofactor-disable.html",
                                                                         success_url="user-settings")))
login = anonymous_required(LoginView.as_view())
setup_view = elevate_required(TwoFactorSetupView.as_view())
qrcode_view = elevate_required(core.QRGeneratorView.as_view())
