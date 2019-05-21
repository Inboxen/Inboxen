##
#    Copyright (C) 2013-2015 Jessica Tallon & Matt Molyneaux
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

from braces.views import LoginRequiredMixin
from django.http import Http404
from django.urls import Resolver404, resolve, reverse, reverse_lazy
from django.views import generic

from inboxen import forms
from inboxen.models import Inbox

__all__ = ["InboxEditView", "FormInboxEditView", "InboxDisownView"]


class InboxEditView(LoginRequiredMixin, generic.UpdateView):
    form_class = forms.InboxEditForm
    template_name = "inboxen/inbox/edit.html"
    success_views = ["user-home", "unified-inbox", "single-inbox"]

    def get_form_kwargs(self):
        kwargs = super(InboxEditView, self).get_form_kwargs()
        kwargs.setdefault("request", self.request)
        return kwargs

    def get_object(self, *args, **kwargs):
        inbox = Inbox.objects.viewable(self.request.user).select_related("domain")
        inbox = inbox.filter(inbox=self.kwargs["inbox"], domain__domain=self.kwargs["domain"])

        try:
            return inbox.get()
        except Inbox.DoesNotExist:
            raise Http404

    def get_success_url(self):
        referer = self.request.META.get("HTTP_REFERER", "/user/home/")
        try:
            url_name = resolve(referer).url_name
            self.success_views.index(url_name)
            return referer
        except (ValueError, Resolver404):
            return reverse("user-home")


class FormInboxEditView(InboxEditView):
    template_name = "inboxen/forms/inbox/edit.html"

    def form_valid(self, form):
        response = super(FormInboxEditView, self).form_valid(form)
        response.status_code = 204

        return response


class InboxDisownView(LoginRequiredMixin, generic.UpdateView):
    template_name = "inboxen/inbox/disown.html"
    form_class = forms.InboxDisownForm
    success_url = reverse_lazy("user-home")

    def get_object(self, *args, **kwargs):
        inbox = Inbox.objects.viewable(self.request.user).select_related("domain")
        inbox = inbox.filter(inbox=self.kwargs["inbox"], domain__domain=self.kwargs["domain"])

        try:
            return inbox.get()
        except Inbox.DoesNotExist:
            raise Http404

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.setdefault("request", self.request)
        return kwargs
