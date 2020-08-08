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

from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from elevate.mixins import ElevateMixin
from elevate.views import ElevateView
from two_factor.utils import default_device

from inboxen.account import forms


class GeneralSettingsView(LoginRequiredMixin, generic.FormView):
    """General settings view"""
    form_class = forms.SettingsForm
    success_url = reverse_lazy("user-settings")
    template_name = "account/index.html"

    def get_form_kwargs(self, **kwargs):
        kwargs = super(GeneralSettingsView, self).get_form_kwargs(**kwargs)
        kwargs.setdefault("request", self.request)
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        form.save()
        return super(GeneralSettingsView, self).form_valid(form=form, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        try:
            backup_tokens = self.request.user.staticdevice_set.all()[0].token_set.count()
        except Exception:
            backup_tokens = 0

        data["backup_tokens"] = backup_tokens
        data["default_device"] = default_device(self.request.user)

        return data


class UsernameChangeView(LoginRequiredMixin, ElevateMixin, generic.FormView):
    """Allow users to change their username"""
    form_class = forms.UsernameChangeForm
    success_url = reverse_lazy("user-settings")
    template_name = "account/username.html"

    def get_form_kwargs(self, **kwargs):
        kwargs = super(UsernameChangeView, self).get_form_kwargs(**kwargs)
        kwargs.setdefault("instance", self.request.user)
        kwargs["initial"] = {"username": ""}  # override initial value for username
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        form.save()
        return super(UsernameChangeView, self).form_valid(form=form, *args, **kwargs)


class PasswordChangeView(auth_views.PasswordChangeView):  # PasswordChangeView already checks loggedin-ness
    form_class = forms.PlaceHolderPasswordChangeForm
    success_url = reverse_lazy('user-settings')
    template_name = 'account/password.html'


class LogoutView(auth_views.LogoutView):
    next_page = "/"


class InboxenElevateView(ElevateView):
    form_class = forms.PlaceHolderSudoForm

    def handle_elevate(self, request, redirect_to, context):
        context['form'].request = request
        return super().handle_elevate(request, redirect_to, context)
