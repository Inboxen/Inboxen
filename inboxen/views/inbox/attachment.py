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

from csp.decorators import csp_replace

from inboxen import models
from inboxen.views import base

HEADER_PARAMS = re.compile(r'([a-zA-Z0-9]+)=["\']?([^"\';=]+)["\']?[;]?')
HEADER_CLEAN = re.compile(r'\s+')

__all__ = ["AttachmentDownloadView"]


class AttachmentDownloadView(base.LoginRequiredMixin, generic.detail.BaseDetailView):
    file_attachment = False
    file_status = 200

    def get_object(self):
        qs = models.PartList.objects.select_related('body')
        qs = qs.filter(email__flags=~models.Email.flags.deleted)

        try:
            return qs.get(id=self.kwargs["attachmentid"], email__inbox__user=self.request.user)
        except models.PartList.DoesNotExist:
            raise Http404

    # csp should allow images, media, and style sheets over https.
    # *Do not* do the same for script-src, that will make bypassing CPS on the
    # rest of the site trivial!
    @csp_replace(STYLE_SRC=["'self'", "'unsafe-inline'", "https:"], IMG_SRC=["'self'", "https:"], MEDIA_SRC=["https:"])
    def get(self, *args, **kwargs):
        if kwargs.get("method", "download") == "download":
            self.file_attachment = True

        return super(AttachmentDownloadView, self).get(*args, **kwargs)

    def render_to_response(self, context):
        # build the Content-Disposition header
        disposition = []
        if self.file_attachment:
            disposition.append("attachment")

        headers = self.object.header_set.get_many("Content-Type", "Content-Disposition")
        content_type = headers.pop("Content-Type", "text/plain").split(";", 1)
        dispos = headers.pop("Content-Disposition", "")

        try:
            params = dict(HEADER_PARAMS.findall(content_type[1]))
        except IndexError:
            params = {}
        params.update(dict(HEADER_PARAMS.findall(dispos)))

        if "filename" in params:
            disposition.append("filename={0}".format(params["filename"]))
        elif "name" in params:
            disposition.append("filename={0}".format(params["name"]))

        disposition = "; ".join(disposition)

        if "charset" in params:
            content_type = "{0}; charset={1}".format(content_type[0], params["charset"])
        else:
            content_type = content_type[0]

        # make header object
        data = self.object.body.data or ""
        response = HttpResponse(
            content=data,
            status=self.file_status
        )

        response["Content-Length"] = self.object.body.size or len(data)
        response["Content-Disposition"] = HEADER_CLEAN.sub(" ", disposition)
        response["Content-Type"] = HEADER_CLEAN.sub(" ", content_type)

        return response
