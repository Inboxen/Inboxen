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

from django import http
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _
from django.views import generic

from django_otp.plugins.otp_totp.models import TOTPDevice

from website import forms
from website.views import base

__all__ = ["TwoFactorView"]

class TwoFactorView(base.CommonContextMixin, base.LoginRequiredMixin, generic.UpdateView):
    form_class = forms.TwoFactorForm
    success_url = reverse_lazy('user-otp')
    headline = _("")
    template_name = "user/settings/otp.html"

    def get_object(self, queryset=None):
        try:
            return self.request.user.totpdevice_set.get()
        except TOTPDevice.DoesNotExist:
            return None

    def form_valid(self, form, *args, **kwargs):
        output = super(TwoFactorView, self).form_valid(form, *args, **kwargs)
        messages.success(self.request, _("Fetching all your data. This may take a while, so check back later!"))
        return output
