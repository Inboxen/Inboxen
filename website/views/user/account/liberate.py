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

from django import http
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _
from django.views import generic

from inboxen import models
from queue.liberate.tasks import TAR_TYPES
from website import forms
from website.views import base

__all__ = ["LiberationView", "LiberationDownloadView"]

class LiberationView(base.CommonContextMixin, base.LoginRequiredMixin, generic.UpdateView):
    form_class = forms.LiberationForm
    success_url = reverse_lazy('user-home')
    headline = _("Liberate your data")
    template_name = "user/account/liberate.html"

    def get_object(self, queryset=None):
        return self.request.user.liberation

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(LiberationView, self).get_form_kwargs(*args, **kwargs)
        kwargs.setdefault("user", self.request.user)
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        output = super(LiberationView, self).form_valid(form, *args, **kwargs)
        messages.success(self.request, _("Fetching all your data. This may take a while, so check back later!"))
        return output

class LiberationDownloadView(base.LoginRequiredMixin, generic.detail.BaseDetailView):
    def get_object(self):
        return self.request.user.liberation

    def render_to_response(self, context):
        content_type = TAR_TYPES[str(self.object.content_type)]["mime-type"]

        disposition = "attachment; filename=liberated_data.{ext}"
        disposition = disposition.format(ext=TAR_TYPES[str(self.object.content_type)]["ext"])

        response = http.HttpResponse(
            content=self.object.payload,
            status=200
        )

        response["Content-Length"] = self.object.size or len(self.object.payload)
        response["Content-Disposition"] = disposition
        response["Content-Type"] = content_type
        return response
