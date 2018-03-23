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

from django.core.urlresolvers import reverse_lazy
from django.views import generic

from braces.views import LoginRequiredMixin
from elevate.mixins import ElevateMixin

from account import forms


__all__ = ["GeneralSettingsView", "UsernameChangeView"]


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


class UsernameChangeView(LoginRequiredMixin, ElevateMixin, generic.FormView):
    """Allow users to change their username"""
    form_class = forms.UsernameChangeForm
    success_url = reverse_lazy("user-settings")
    template_name = "account/username.html"

    def get_form_kwargs(self, **kwargs):
        kwargs = super(UsernameChangeView, self).get_form_kwargs(**kwargs)
        kwargs.setdefault("instance", self.request.user)
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        form.save()
        return super(UsernameChangeView, self).form_valid(form=form, *args, **kwargs)
