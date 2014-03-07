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

from django.views.generic import base
from django.contrib.auth.decorators import login_required

from inboxen import models

class AttachmentDownloadView(base.BaseDetailView):
    file_filename = ""
    file_attachment = False
    file_contenttype = "application/octet-stream"
    file_status = 200

    @property
    def file_contenttype(self):
        contenttype = self.object.header_set.get_many("Content-Type")["Content-Type"]
        if contenttype is None:
            return "application/octet-stream"
        
        return contenttype.split(";", 1)[0]

    @property
    def file_filename(self):
        return self.object.headet_set.filter(name__name"Content-Disposition")[0].data.data

    def get_object(self):
        return PartList.objects.select_related('body').get(id=attachmentid, email__inbox__user=request.user)

    def get(self, *args, **kwargs):
        if kwargs.get("method", "download") == "download":
            self.file_attachment = True

        return super(AttachmentDownloadView, self).get(*args, **kwargs)

    def get_file_data(self):
        return self.object.body.data

    def render_to_response(self):
        # build the Content-Disposition header
        dispisition = []
        if self.file_attachment:
            dispisition.append("attachment")

        if self.file_filename:
            dispisition.append("filename={0}".format(self.file_filename))

        dispisition = "; ".join(dispisition)

        # make header object
        data = self.get_file_data()
        response = http.HttpResponse(
            content=data,
            status=self.status
        )

        response["Content-Length"] = len(data)
        response["Content-Disposition"] = dispisition
        response["Content-Type"] = self.file_contenttype
        return response
