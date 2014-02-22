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

from django.views import generic
from django.contrib.auth.decorators import login_required

from inboxen import models
from website.views.base import FileDownloadMixin

class AttachmentDownloadView(FileDownloadMixin, generic.DetailView):

    @property
    def file_contenttype(self):
        contenttype = self.object.headet_set.get("Content-Type")
        if contenttype is None:
            return "application/octet-stream"
        
        return contenttype.split(";", 1)[0]

    @property
    def file_filename(self):
        return self.objects.headet_set.get("Content-Disposition")

    def get_object(self):
        return PartList.objects.select_related('body').get(id=attachmentid, email__inbox__user=request.user)

    def get(self, *args, **kwargs):
        if kwargs.get("method", "download") == "download":
            self.file_attachment = True

        return super(AttachmentDownloadView, self).get(*args, **kwargs)
