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
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from django.views import generic

from braces.views import LoginRequiredMixin
from sendfile import sendfile

from inboxen.liberation import forms
from inboxen.liberation.tasks import TAR_TYPES


__all__ = ["LiberationView", "LiberationDownloadView"]


class LiberationView(LoginRequiredMixin, generic.UpdateView):
    form_class = forms.LiberationForm
    success_url = reverse_lazy('user-home')
    template_name = "liberation/liberate.html"

    def get_object(self, queryset=None):
        return self.request.user.liberation

    def get_form_kwargs(self, **kwargs):
        kwargs = super(LiberationView, self).get_form_kwargs(**kwargs)
        kwargs.setdefault("user", self.request.user)
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        output = super(LiberationView, self).form_valid(form, *args, **kwargs)
        messages.success(self.request, _("Fetching all your data. This may take a while, so check back later!"))
        return output


class LiberationDownloadView(LoginRequiredMixin, generic.detail.BaseDetailView):
    def get_object(self):
        liberation = self.request.user.liberation

        if liberation.path is None:
            raise http.Http404

        return liberation

    def render_to_response(self, context):
        content_type = TAR_TYPES[str(self.object.content_type)]["mime-type"]

        filename = "liberated_data.{ext}".format(ext=TAR_TYPES[str(self.object.content_type)]["ext"])

        response = sendfile(
            request=self.request,
            filename=self.object.path,
            attachment=True,
            attachment_filename=filename,
            mimetype=content_type
        )
        del response["Content-Encoding"]
        return response
