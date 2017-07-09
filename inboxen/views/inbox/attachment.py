##
#    Copyright (C) 2013 Jessica Tallon & Matthew Molyneaux
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

import re

from django.http import Http404, HttpResponse
from django.views import generic

from braces.views import LoginRequiredMixin

from inboxen import models

HEADER_PARAMS = re.compile(r'([a-zA-Z0-9]+)=["\']?([^"\';=]+)["\']?[;]?')
HEADER_CLEAN = re.compile(r'\s+')

__all__ = ["AttachmentDownloadView"]


class AttachmentDownloadView(LoginRequiredMixin, generic.detail.BaseDetailView):
    def get_object(self):
        qs = models.PartList.objects.select_related('body')
        qs = qs.filter(email__flags=~models.Email.flags.deleted, email__inbox__user=self.request.user)

        try:
            return qs.get(id=self.kwargs["attachmentid"])
        except models.PartList.DoesNotExist:
            raise Http404

    def render_to_response(self, context):
        # build the Content-Disposition header
        disposition = ["attachment"]

        if self.object.filename:
            disposition.append("filename=\"{0}\"".format(self.object.filename.encode("utf8")))

        disposition = "; ".join(disposition)

        if self.object.content_type:
            content_type = "{0}; charset={1}".format(
                self.object.content_type.encode("utf8"),
                self.object.charset.encode("utf8"),
            )
        else:
            content_type = "application/octet-stream"

        # make header object
        data = self.object.body.data or ""
        response = HttpResponse(
            content=data,
            status=200,
        )

        response["Content-Length"] = self.object.body.size or len(data)
        response["Content-Disposition"] = HEADER_CLEAN.sub(" ", disposition)
        response["Content-Type"] = HEADER_CLEAN.sub(" ", content_type)

        return response
